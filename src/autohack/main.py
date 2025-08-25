"""
前后端分离的启动脚本
自动管理后端服务器的启动和前端客户端的连接
"""

import os
import sys
import asyncio
import argparse
import subprocess
import time
import atexit
from typing import Optional

from autohack.core.constant import VERSION, VERSION_ID


class AutoHackManager:
    def __init__(self):
        self.backend_process: Optional[subprocess.Popen] = None
        self.server_host = "127.0.0.1"
        self.server_port = 8000

    def start_backend(self, debug: bool = False) -> bool:
        """启动后端服务器"""
        try:
            # 检查是否已经有服务器在运行
            if self.is_server_running():
                print("Backend server is already running.")
                return True

            # 启动后端服务器
            cmd = [
                sys.executable,
                "-m",
                "autohack.backend.server",
                "--host",
                self.server_host,
                "--port",
                str(self.server_port),
            ]

            if debug:
                print(f"Starting backend server: {' '.join(cmd)}")

            self.backend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL if not debug else None,
                stderr=subprocess.DEVNULL if not debug else None,
                cwd=os.getcwd(),
            )

            # 等待服务器启动
            for i in range(30):  # 最多等待30秒
                if self.is_server_running():
                    if debug:
                        print("Backend server started successfully.")
                    return True
                time.sleep(1)

            print("Failed to start backend server.")
            return False

        except Exception as e:
            print(f"Error starting backend server: {e}")
            return False

    def stop_backend(self):
        """停止后端服务器"""
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            self.backend_process = None

    def is_server_running(self) -> bool:
        """检查服务器是否在运行"""
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.server_host, self.server_port))
            sock.close()
            return result == 0
        except:
            return False

    async def run_frontend(self, debug: bool = False):
        """运行前端客户端"""
        from autohack.frontend.client import AutoHackClient

        server_url = f"ws://{self.server_host}:{self.server_port}"
        client = AutoHackClient(server_url)

        await client.run(debug)

    async def run(self, debug: bool = False, standalone_server: bool = False):
        """运行完整的应用"""
        # 注册退出处理函数
        atexit.register(self.stop_backend)

        if not standalone_server:
            # 启动后端服务器
            if not self.start_backend(debug):
                print("Failed to start backend server.")
                sys.exit(1)

        try:
            # 运行前端客户端
            await self.run_frontend(debug)
        finally:
            if not standalone_server:
                self.stop_backend()


def check_dependencies():
    """检查依赖项"""
    missing_deps = []

    try:
        import fastapi
    except ImportError:
        missing_deps.append("fastapi")

    try:
        import uvicorn
    except ImportError:
        missing_deps.append("uvicorn")

    try:
        import websockets
    except ImportError:
        missing_deps.append("websockets")

    if missing_deps:
        print("Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nPlease install them with:")
        print(f"  pip install {' '.join(missing_deps)}")
        return False

    return True


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        prog="autohack",
        description="autohack-next - Automated hack data generator (Frontend-Backend)",
    )
    parser.add_argument(
        "--version", action="store_true", help="Show version information"
    )
    parser.add_argument("--version-id", action="store_true", help="Show version ID")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--server-only", action="store_true", help="Run backend server only"
    )
    parser.add_argument(
        "--client-only",
        action="store_true",
        help="Run frontend client only (assumes server is running)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Backend server host")
    parser.add_argument("--port", type=int, default=8000, help="Backend server port")

    args = parser.parse_args()

    if args.version:
        sys.stdout.write(f"{VERSION}\n")
        sys.exit(0)

    if args.version_id:
        sys.stdout.write(f"{VERSION_ID}\n")
        sys.exit(0)

    # 检查依赖项
    if not check_dependencies():
        sys.exit(1)

    manager = AutoHackManager()
    manager.server_host = args.host
    manager.server_port = args.port

    try:
        if args.server_only:
            # 只运行后端服务器
            from autohack.backend.server import run_server

            print(f"Starting backend server on {args.host}:{args.port}")
            await run_server(args.host, args.port)
        elif args.client_only:
            # 只运行前端客户端
            await manager.run_frontend(args.debug)
        else:
            # 运行完整应用（默认）
            await manager.run(args.debug)

    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(0)
    except Exception as e:
        import traceback

        print(f"Unhandled exception: {e}")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)
    finally:
        manager.stop_backend()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
