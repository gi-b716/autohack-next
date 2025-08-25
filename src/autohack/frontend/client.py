"""
前端客户端
负责命令行输出及用户交互
"""

import asyncio
import json
import sys
import time
import uuid
import argparse
from typing import Dict, Any, Optional

try:
    import websockets
except ImportError:
    websockets = None

from autohack.core.constant import VERSION


class AutoHackClient:
    def __init__(self, server_url: str = "ws://127.0.0.1:8000"):
        self.server_url = server_url
        self.client_id = str(uuid.uuid4())
        self.websocket = None
        self.running = False
        self.debug = False

        # 状态变量
        self.initialized = False
        self.hack_running = False
        self.data_count = 0
        self.error_count = 0
        self.last_stats_time = 0

    async def connect(self):
        """连接到后端服务器"""
        try:
            import websockets

            self.websocket = await websockets.connect(
                f"{self.server_url}/ws/{self.client_id}"
            )
            return True
        except ImportError:
            print(
                "Error: websockets library not available. Please install it with: pip install websockets"
            )
            return False
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False

    async def send_message(self, message: Dict[str, Any]):
        """发送消息到后端"""
        if self.websocket:
            await self.websocket.send(json.dumps(message))

    async def receive_message(self):
        """接收来自后端的消息"""
        if self.websocket:
            try:
                message = await self.websocket.recv()
                return json.loads(message)
            except Exception as e:
                if self.debug:
                    print(f"Error receiving message: {e}")
                return None
        return None

    async def handle_messages(self):
        """处理来自后端的消息"""
        while self.running:
            message = await self.receive_message()
            if message is None:
                break

            message_type = message.get("type")
            data = message.get("data", {})

            if message_type == "init_success":
                await self.handle_init_success(data)
            elif message_type == "status_update":
                await self.handle_status_update(data)
            elif message_type == "progress_update":
                await self.handle_progress_update(data)
            elif message_type == "statistics_update":
                await self.handle_statistics_update(data)
            elif message_type == "error_found":
                await self.handle_error_found(data)
            elif message_type == "completed":
                await self.handle_completed(data)
            elif message_type == "error":
                await self.handle_error(data)
            elif message_type == "warning":
                await self.handle_warning(data)
            elif message_type == "stopped":
                await self.handle_stopped(data)
            elif message_type == "record_saved":
                await self.handle_record_saved(data)

    async def handle_init_success(self, data: Dict[str, Any]):
        """处理初始化成功"""
        self.initialized = True
        client_id = data.get("client_id")
        version = data.get("version")
        hack_data_path = data.get("hack_data_path")
        storage_path = data.get("storage_path")
        log_file = data.get("log_file")
        symlink_fallback = data.get("symlink_fallback", False)

        sys.stdout.write(f"autohack-next {version} - Client ID: {client_id}\n")

        if symlink_fallback:
            sys.stdout.write(
                "Hack data folder symlink creation failed. Using fallback method.\n"
            )

        sys.stdout.write(
            f"Hack data storaged to {hack_data_path}.\n"
            f"{' '*18}and {storage_path}\n"
            f"Log file: {log_file}\n\n"
        )

    async def handle_status_update(self, data: Dict[str, Any]):
        """处理状态更新"""
        stage = data.get("stage")
        message = data.get("message")

        if stage == "compiling":
            sys.stdout.write(f"\x1b[1K\r{message}")
        elif stage == "compiled":
            sys.stdout.write(f"\x1b[1K\r{message}.\n")
        elif stage == "running":
            sys.stdout.write(f"\n{message}\n")

    async def handle_progress_update(self, data: Dict[str, Any]):
        """处理进度更新"""
        data_count = data.get("data_count", 0)
        error_count = data.get("error_count", 0)
        stage = data.get("stage")

        self.data_count = data_count
        self.error_count = error_count

        stage_messages = {
            "generating_input": "Generate input.",
            "generating_answer": "Generate answer.",
            "running_source": "Run source code.",
        }

        message = stage_messages.get(stage or "", "Processing...")
        sys.stdout.write(f"\x1b[2K\r{data_count}: {message}")

    async def handle_statistics_update(self, data: Dict[str, Any]):
        """处理统计信息更新"""
        elapsed_time = data.get("elapsed_time", 0)
        avg_speed = data.get("avg_speed", 0)
        time_per_data = data.get("time_per_data", 0)
        progress_percent = data.get("progress_percent")

        progress_str = (
            f" ({progress_percent:.0f}%)" if progress_percent is not None else ""
        )

        sys.stdout.write(
            f"\n\x1b[2K\rTime taken: {elapsed_time:.2f} seconds, "
            f"average {avg_speed:.2f} data per second, "
            f"{time_per_data:.2f} second per data.{progress_str}\x1b[1A"
        )

    async def handle_error_found(self, data: Dict[str, Any]):
        """处理发现错误"""
        error_number = data.get("error_number")
        data_number = data.get("data_number")
        message = data.get("message")

        sys.stdout.write(f"\x1b[2K\r[{error_number}]: {message}\n")

    async def handle_completed(self, data: Dict[str, Any]):
        """处理完成"""
        self.hack_running = False
        total_data = data.get("total_data", 0)
        error_data = data.get("error_data", 0)
        total_time = data.get("total_time", 0)
        avg_speed = data.get("avg_speed", 0)
        time_per_data = data.get("time_per_data", 0)

        sys.stdout.write(
            f"\x1b[2K\rFinished. {total_data} data generated, {error_data} error data found.\n"
            f"\x1b[2K\rTime taken: {total_time:.2f} seconds, "
            f"average {avg_speed:.2f} data per second, "
            f"{time_per_data:.2f} second per data.\n"
        )

        if error_data == 0:
            sys.stdout.write("No error data found. Hack data folder removed.\n")

    async def handle_error(self, data: Dict[str, Any]):
        """处理错误"""
        message = data.get("message")
        error_type = data.get("error_type")

        if error_type == "compilation_error":
            file_name = data.get("file_name", "unknown")
            sys.stdout.write(f"\r{message}\n\x1b[?25h")
        else:
            sys.stdout.write(f"\x1b[2K\r{message}\n\x1b[?25h")

        self.hack_running = False

    async def handle_warning(self, data: Dict[str, Any]):
        """处理警告"""
        message = data.get("message")
        sys.stdout.write(f"Warning: {message}\n")

    async def handle_stopped(self, data: Dict[str, Any]):
        """处理停止"""
        self.hack_running = False
        message = data.get("message", "Process stopped")
        sys.stdout.write(f"\x1b[2K\r{message}\n\x1b[?25h")

    async def handle_record_saved(self, data: Dict[str, Any]):
        """处理记录保存"""
        record_path = data.get("record_path")
        sys.stdout.write(f"Record saved to {record_path}.\n\x1b[?25h")

    async def initialize(self, debug: bool = False):
        """初始化"""
        self.debug = debug

        await self.send_message({"type": "init", "data": {"debug": debug}})

    async def start_hack(self):
        """开始对拍"""
        if not self.initialized:
            print("Not initialized")
            return False

        if self.hack_running:
            print("Already running")
            return False

        self.hack_running = True
        await self.send_message({"type": "start"})
        return True

    async def stop_hack(self):
        """停止对拍"""
        if self.hack_running:
            await self.send_message({"type": "stop"})

    async def save_record(self, comment: str = ""):
        """保存记录"""
        # 发送保存记录的消息给后端
        await self.send_message({"type": "save_record", "data": {"comment": comment}})

    async def run(self, debug: bool = False):
        """运行客户端"""
        self.running = True

        # 隐藏光标
        sys.stdout.write("\x1b[?25l")

        if debug:
            sys.stdout.write("Debug mode enabled. Logging level set to DEBUG.\n")

        # 连接到服务器
        if not await self.connect():
            sys.exit(1)

        # 初始化
        await self.initialize(debug)

        # 启动消息处理任务
        message_task = asyncio.create_task(self.handle_messages())

        # 等待初始化完成
        while not self.initialized and self.running:
            await asyncio.sleep(0.1)

        if not self.running:
            return

        # 倒计时
        for i in range(3):
            sys.stdout.write(f"\x1b[1K\rStarting in {3-i} seconds...")
            await asyncio.sleep(1)

        # 开始对拍
        await self.start_hack()

        # 等待完成或中断
        try:
            while self.hack_running and self.running:
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            await self.stop_hack()
            sys.stdout.write("\x1b[1;31mProcess interrupted by user.\n\x1b[?25h\x1b[0m")
            return

        # 获取用户评论
        sys.stdout.write("\n")
        sys.stdout.write("\x1b[?25h")  # 显示光标
        try:
            comment = input("Comment (optional): ")
            sys.stdout.write("\x1b[?25l")  # 隐藏光标
            await self.save_record(comment)
        except KeyboardInterrupt:
            sys.stdout.write(
                "\x1b[1;31m\nProcess interrupted by user.\n\x1b[?25h\x1b[0m"
            )
            return

        # 等待记录保存完成
        await asyncio.sleep(0.5)

        # 清理
        message_task.cancel()
        if self.websocket:
            await self.websocket.close()


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        prog="autohack",
        description="autohack-next - Automated hack data generator (Client)",
    )
    parser.add_argument(
        "--version", action="store_true", help="Show version information"
    )
    parser.add_argument("--version-id", action="store_true", help="Show version ID")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with DEBUG logging level",
    )
    parser.add_argument(
        "--server", default="ws://127.0.0.1:8000", help="Backend server URL"
    )

    args = parser.parse_args()

    if args.version:
        sys.stdout.write(f"{VERSION}\n")
        sys.exit(0)

    if args.version_id:
        from autohack.core.constant import VERSION_ID

        sys.stdout.write(f"{VERSION_ID}\n")
        sys.exit(0)

    client = AutoHackClient(args.server)

    try:
        await client.run(args.debug)
    except KeyboardInterrupt:
        sys.stdout.write("\x1b[1;31mProcess interrupted by user.\n\x1b[?25h\x1b[0m")
        sys.exit(0)
    except Exception as e:
        import traceback
        import os

        sys.stdout.write(f"\x1b[1;31mUnhandled exception.\n")
        error_file_path = os.path.join(
            os.getcwd(), f"autohack-error.{time.time():.0f}.log"
        )
        open(error_file_path, "w+").write(repr(e))
        sys.stdout.write(
            f"\x1b[1;31mError details saved to {error_file_path}.\x1b[0m\n\n"
        )
        traceback.print_exc()
        sys.stdout.write("\x1b[?25h")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
