"""
后端服务器
负责客户端ID生成、初始化、执行主要对拍逻辑
"""

import asyncio
import uuid
import time
import os
import shutil
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging

from autohack.core.constant import *
from autohack.core.exception import *
from autohack.core.path import *
from autohack.core.util import *
from autohack.lib.config import *
from autohack.lib.logger import *
from autohack.checker import *
from autohack.function import *


class AutoHackBackend:
    def __init__(self):
        self.app = FastAPI(title="AutoHack Backend", version=VERSION)
        self.clients: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}

        # 添加CORS中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 设置路由
        self.setup_routes()

    def setup_routes(self):
        @self.app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: str):
            await self.handle_websocket(websocket, client_id)

    async def handle_websocket(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.clients[client_id] = websocket

        try:
            while True:
                data = await websocket.receive_json()
                await self.process_message(client_id, data)
        except WebSocketDisconnect:
            if client_id in self.clients:
                del self.clients[client_id]
            if client_id in self.sessions:
                del self.sessions[client_id]

    async def process_message(self, client_id: str, message: Dict[str, Any]):
        """处理来自前端的消息"""
        message_type = message.get("type")

        if message_type == "init":
            await self.handle_init(client_id, message.get("data", {}))
        elif message_type == "start":
            await self.handle_start(client_id)
        elif message_type == "stop":
            await self.handle_stop(client_id)
        elif message_type == "get_status":
            await self.handle_get_status(client_id)
        elif message_type == "save_record":
            await self.handle_save_record(client_id, message.get("data", {}))

    async def handle_init(self, client_id: str, data: Dict[str, Any]):
        """初始化会话"""
        try:
            # 检查目录
            checkDirectoryExists(DATA_FOLDER_PATH)
            checkDirectoryExists(LOG_FOLDER_PATH)
            checkDirectoryExists(TEMP_FOLDER_PATH)
            if mswindows():
                os.system("attrib +h {0}".format(DATA_FOLDER_PATH))

            # 初始化日志
            debug_mode = data.get("debug", False)
            logger_object = Logger(
                LOG_FOLDER_PATH,
                logging.DEBUG if debug_mode else logging.INFO,
            )
            logger = logger_object.getLogger()

            # 初始化配置
            config = Config(CONFIG_FILE_PATH, logger)

            # 记录初始化信息
            logger.info(f'[autohack] Data folder path: "{DATA_FOLDER_PATH}"')
            logger.info(f"[autohack] Client ID: {client_id}")
            logger.info(f"[autohack] Initialized. Version: {VERSION}")

            # 设置hack数据文件夹
            symlink_fallback = False
            checkDirectoryExists(getHackDataStorageFolderPath(client_id))
            if os.path.islink(CURRENT_HACK_DATA_FOLDER_PATH):
                os.unlink(CURRENT_HACK_DATA_FOLDER_PATH)
            elif os.path.isdir(CURRENT_HACK_DATA_FOLDER_PATH):
                shutil.rmtree(CURRENT_HACK_DATA_FOLDER_PATH)

            try:
                os.symlink(
                    getHackDataStorageFolderPath(client_id),
                    CURRENT_HACK_DATA_FOLDER_PATH,
                    target_is_directory=True,
                )
            except OSError:
                symlink_fallback = True
                logger.warning(
                    "[autohack] Symlink creation failed. Using fallback method."
                )
                checkDirectoryExists(CURRENT_HACK_DATA_FOLDER_PATH)

            # 保存会话信息
            self.sessions[client_id] = {
                "logger": logger,
                "logger_object": logger_object,
                "config": config,
                "symlink_fallback": symlink_fallback,
                "initialized": True,
                "running": False,
                "data_count": 0,
                "error_data_count": 0,
                "start_time": None,
            }

            await self.send_message(
                client_id,
                {
                    "type": "init_success",
                    "data": {
                        "client_id": client_id,
                        "version": VERSION,
                        "hack_data_path": CURRENT_HACK_DATA_FOLDER_PATH,
                        "storage_path": getHackDataStorageFolderPath(client_id),
                        "log_file": logger_object.getLogFilePath(),
                        "symlink_fallback": symlink_fallback,
                    },
                },
            )

        except Exception as e:
            await self.send_message(
                client_id,
                {
                    "type": "error",
                    "data": {"message": str(e), "error_type": "init_error"},
                },
            )

    async def handle_start(self, client_id: str):
        """开始对拍进程"""
        if client_id not in self.sessions:
            await self.send_message(
                client_id,
                {
                    "type": "error",
                    "data": {
                        "message": "Session not initialized",
                        "error_type": "session_error",
                    },
                },
            )
            return

        session = self.sessions[client_id]
        if session.get("running"):
            await self.send_message(
                client_id,
                {
                    "type": "error",
                    "data": {"message": "Already running", "error_type": "state_error"},
                },
            )
            return

        session["running"] = True
        session["data_count"] = 0
        session["error_data_count"] = 0
        session["start_time"] = time.time()

        # 在后台运行对拍进程
        asyncio.create_task(self.run_hack_process(client_id))

    async def run_hack_process(self, client_id: str):
        """运行对拍进程的主逻辑"""
        session = self.sessions[client_id]
        config = session["config"]
        logger = session["logger"]

        try:
            # 编译阶段
            await self.send_message(
                client_id,
                {
                    "type": "status_update",
                    "data": {"stage": "compiling", "message": "开始编译..."},
                },
            )

            file_list = [
                [config.getConfigEntry("commands.compile.source"), "source code"],
                [config.getConfigEntry("commands.compile.std"), "standard code"],
                [config.getConfigEntry("commands.compile.generator"), "generator code"],
            ]

            for file_info in file_list:
                await self.send_message(
                    client_id,
                    {
                        "type": "status_update",
                        "data": {
                            "stage": "compiling",
                            "message": f"编译 {file_info[1]}...",
                        },
                    },
                )

                try:
                    compileCode(file_info[0], file_info[1])
                    logger.debug(
                        f"[autohack] {file_info[1].capitalize()} compiled successfully."
                    )
                except CompilationError as e:
                    logger.error(
                        f"[autohack] {e.fileName.capitalize()} compilation failed: {e}"
                    )
                    await self.send_message(
                        client_id,
                        {
                            "type": "error",
                            "data": {
                                "message": str(e),
                                "error_type": "compilation_error",
                                "file_name": e.fileName,
                            },
                        },
                    )
                    session["running"] = False
                    return

            await self.send_message(
                client_id,
                {
                    "type": "status_update",
                    "data": {"stage": "compiled", "message": "编译完成"},
                },
            )

            # 获取配置参数
            data_count = 0
            error_data_count = 0
            generate_command = config.getConfigEntry("commands.run.generator")
            std_command = config.getConfigEntry("commands.run.std")
            source_command = config.getConfigEntry("commands.run.source")
            time_limit = config.getConfigEntry("time_limit") / 1000
            memory_limit = config.getConfigEntry("memory_limit") * 1024 * 1024
            input_file_path = config.getConfigEntry("paths.input")
            answer_file_path = config.getConfigEntry("paths.answer")
            output_file_path = config.getConfigEntry("paths.output")
            maximum_data_limit = config.getConfigEntry("maximum_number_of_data")
            error_data_limit = config.getConfigEntry("error_data_number_limit")
            refresh_speed = config.getConfigEntry("refresh_speed")

            last_status_error = False

            await self.send_message(
                client_id,
                {
                    "type": "status_update",
                    "data": {"stage": "running", "message": "开始生成测试数据..."},
                },
            )

            # 主循环
            while (
                (maximum_data_limit <= 0 or data_count < maximum_data_limit)
                and (error_data_limit <= 0 or error_data_count < error_data_limit)
                and session.get("running", False)
            ):

                data_count += 1
                session["data_count"] = data_count

                # 生成输入数据
                await self.send_message(
                    client_id,
                    {
                        "type": "progress_update",
                        "data": {
                            "data_count": data_count,
                            "error_count": error_data_count,
                            "stage": "generating_input",
                        },
                    },
                )

                try:
                    logger.debug(f"[autohack] Generating data {data_count}.")
                    data_input = generateInput(generate_command, client_id)
                except InputGenerationError as e:
                    logger.error(f"[autohack] Input generation failed: {e}")
                    await self.send_message(
                        client_id,
                        {
                            "type": "error",
                            "data": {
                                "message": str(e),
                                "error_type": "input_generation_error",
                            },
                        },
                    )
                    session["running"] = False
                    return

                # 生成答案
                await self.send_message(
                    client_id,
                    {
                        "type": "progress_update",
                        "data": {
                            "data_count": data_count,
                            "error_count": error_data_count,
                            "stage": "generating_answer",
                        },
                    },
                )

                try:
                    logger.debug(f"[autohack] Generating answer for data {data_count}.")
                    data_answer = generateAnswer(std_command, data_input, client_id)
                except AnswerGenerationError as e:
                    logger.error(f"[autohack] Answer generation failed: {e}")
                    await self.send_message(
                        client_id,
                        {
                            "type": "error",
                            "data": {
                                "message": str(e),
                                "error_type": "answer_generation_error",
                            },
                        },
                    )
                    session["running"] = False
                    return

                # 运行源代码
                await self.send_message(
                    client_id,
                    {
                        "type": "progress_update",
                        "data": {
                            "data_count": data_count,
                            "error_count": error_data_count,
                            "stage": "running_source",
                        },
                    },
                )

                logger.debug(f"[autohack] Run source code for data {data_count}.")
                result = runSourceCode(
                    source_command, data_input, time_limit, memory_limit
                )

                # 定期更新统计信息
                if data_count % refresh_speed == 0 or last_status_error:
                    last_status_error = False
                    current_time = time.time()
                    start_time = session["start_time"]
                    elapsed_time = current_time - start_time
                    avg_speed = data_count / elapsed_time if elapsed_time > 0 else 0
                    time_per_data = elapsed_time / data_count if data_count > 0 else 0
                    progress_percent = (
                        (data_count * 100 / maximum_data_limit)
                        if maximum_data_limit > 0
                        else None
                    )

                    await self.send_message(
                        client_id,
                        {
                            "type": "statistics_update",
                            "data": {
                                "elapsed_time": elapsed_time,
                                "avg_speed": avg_speed,
                                "time_per_data": time_per_data,
                                "progress_percent": progress_percent,
                            },
                        },
                    )

                # 检查结果
                error_found = False
                error_message = ""
                log_message = ""

                if result.memoryOut:
                    error_found = True
                    error_message = f"Memory limit exceeded for data {data_count}."
                    log_message = (
                        f"[autohack] Memory limit exceeded for data {data_count}."
                    )
                elif result.timeOut:
                    error_found = True
                    error_message = f"Time limit exceeded for data {data_count}."
                    log_message = (
                        f"[autohack] Time limit exceeded for data {data_count}."
                    )
                elif result.returnCode != 0:
                    error_found = True
                    error_message = f"Runtime error for data {data_count} with return code {result.returnCode}."
                    log_message = f"[autohack] Runtime error for data {data_count} with return code {result.returnCode}."
                else:
                    checker_result = basicChecker(result.stdout or b"", data_answer)
                    if not checker_result[0]:
                        error_found = True
                        error_message = (
                            f"Wrong answer for data {data_count}. - {checker_result[1]}"
                        )
                        log_message = f"[autohack] Wrong answer for data {data_count}. Checker output: {checker_result[1]}"

                if error_found:
                    last_status_error = True
                    error_data_count += 1
                    session["error_data_count"] = error_data_count

                    # 保存错误数据
                    self.save_error_data(
                        error_data_count,
                        data_input,
                        data_answer,
                        result.stdout or b"",
                        input_file_path,
                        answer_file_path,
                        output_file_path,
                    )

                    logger.info(log_message)
                    await self.send_message(
                        client_id,
                        {
                            "type": "error_found",
                            "data": {
                                "error_number": error_data_count,
                                "data_number": data_count,
                                "message": error_message,
                            },
                        },
                    )

            # 完成
            session["running"] = False
            end_time = time.time()
            total_time = end_time - session["start_time"]

            await self.send_message(
                client_id,
                {
                    "type": "completed",
                    "data": {
                        "total_data": data_count,
                        "error_data": error_data_count,
                        "total_time": total_time,
                        "avg_speed": data_count / total_time if total_time > 0 else 0,
                        "time_per_data": (
                            total_time / data_count if data_count > 0 else 0
                        ),
                    },
                },
            )

            # 处理结果文件
            if error_data_count > 0:
                if session["symlink_fallback"]:
                    shutil.copytree(
                        CURRENT_HACK_DATA_FOLDER_PATH,
                        getHackDataStorageFolderPath(client_id),
                        dirs_exist_ok=True,
                    )
                    logger.info(
                        f"[autohack] Hack data saved to data storage folder: {getHackDataStorageFolderPath(client_id)}"
                    )
            else:
                shutil.rmtree(getHackDataStorageFolderPath(client_id))
                logger.info("[autohack] No error data found. Hack data folder removed.")

            # 检查存储大小警告
            if (
                os.path.exists(HACK_DATA_STORAGE_FOLDER_PATH)
                and os.path.getsize(HACK_DATA_STORAGE_FOLDER_PATH) > 256 * 1024 * 1024
            ):
                logger.warning(
                    f"[autohack] Hack data storage folder size exceeds 256 MB: {HACK_DATA_STORAGE_FOLDER_PATH}"
                )
                await self.send_message(
                    client_id,
                    {
                        "type": "warning",
                        "data": {
                            "message": f"Hack data storage folder size exceeds 256 MB: {HACK_DATA_STORAGE_FOLDER_PATH}"
                        },
                    },
                )

        except Exception as e:
            logger.error(f"[autohack] Error in hack process: {e}")
            await self.send_message(
                client_id,
                {
                    "type": "error",
                    "data": {"message": str(e), "error_type": "runtime_error"},
                },
            )
        finally:
            session["running"] = False

    def save_error_data(
        self,
        error_count: int,
        data_input: bytes,
        data_answer: bytes,
        data_output: bytes,
        input_path: str,
        answer_path: str,
        output_path: str,
    ):
        """保存错误数据"""
        checkDirectoryExists(getHackDataFolderPath(error_count, input_path))
        checkDirectoryExists(getHackDataFolderPath(error_count, answer_path))
        checkDirectoryExists(getHackDataFolderPath(error_count, output_path))

        open(getHackDataFilePath(error_count, input_path), "wb").write(data_input)
        open(getHackDataFilePath(error_count, answer_path), "wb").write(data_answer)
        open(getHackDataFilePath(error_count, output_path), "wb").write(data_output)

    async def handle_stop(self, client_id: str):
        """停止对拍进程"""
        if client_id in self.sessions:
            self.sessions[client_id]["running"] = False
            await self.send_message(
                client_id,
                {"type": "stopped", "data": {"message": "Process stopped by user"}},
            )

    async def handle_get_status(self, client_id: str):
        """获取当前状态"""
        if client_id not in self.sessions:
            await self.send_message(
                client_id,
                {"type": "status", "data": {"initialized": False, "running": False}},
            )
            return

        session = self.sessions[client_id]
        await self.send_message(
            client_id,
            {
                "type": "status",
                "data": {
                    "initialized": session.get("initialized", False),
                    "running": session.get("running", False),
                    "data_count": session.get("data_count", 0),
                    "error_data_count": session.get("error_data_count", 0),
                },
            },
        )

    async def save_record(self, client_id: str, comment: str = ""):
        """保存记录"""
        if client_id not in self.sessions:
            return

        session = self.sessions[client_id]
        if "start_time" not in session:
            return

        data_count = session.get("data_count", 0)
        error_data_count = session.get("error_data_count", 0)
        start_time = session["start_time"]
        end_time = time.time()
        total_time = end_time - start_time

        record_content = (
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))} / {client_id}\n"
            f"{data_count} data generated, {error_data_count} error data found.\n"
            f"Time taken: {total_time:.2f} seconds, average {data_count/total_time:.2f} data per second, "
            f"{total_time/data_count:.2f} second per data.\n"
            f"{comment}\n\n"
        )

        open(RECORD_FILE_PATH, "a+").write(record_content)
        session["logger"].info(f"[autohack] Record saved to {RECORD_FILE_PATH}.")

        await self.send_message(
            client_id,
            {"type": "record_saved", "data": {"record_path": RECORD_FILE_PATH}},
        )

    async def handle_save_record(self, client_id: str, data: Dict[str, Any]):
        """处理保存记录请求"""
        comment = data.get("comment", "")
        await self.save_record(client_id, comment)

    async def send_message(self, client_id: str, message: Dict[str, Any]):
        """发送消息到前端"""
        if client_id in self.clients:
            try:
                await self.clients[client_id].send_json(message)
            except Exception:
                # 连接已断开
                if client_id in self.clients:
                    del self.clients[client_id]


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    backend = AutoHackBackend()
    return backend.app


async def run_server(host: str = "127.0.0.1", port: int = 8000):
    """运行服务器"""
    import uvicorn

    config = uvicorn.Config(
        "autohack.backend.server:create_app",
        host=host,
        port=port,
        factory=True,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="AutoHack Backend Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")

    args = parser.parse_args()

    try:
        asyncio.run(run_server(args.host, args.port))
    except KeyboardInterrupt:
        print("Server stopped by user")
        sys.exit(0)
