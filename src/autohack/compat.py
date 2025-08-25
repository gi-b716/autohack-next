"""
向后兼容性包装器
在无法使用前后端分离架构时回退到原始版本
"""

import sys
import os


def check_frontend_backend_support():
    """检查是否支持前后端分离"""
    try:
        import fastapi
        import uvicorn
        import websockets

        return True
    except ImportError:
        return False


def run_legacy_mode():
    """运行旧版模式"""
    print("Warning: Running in legacy mode (dependencies not available)")
    print("For full functionality, install: pip install fastapi uvicorn websockets")
    print()

    # 运行原版程序
    os.environ["AUTOHACK_ENTRYPOINT"] = "1"
    from autohack import __main__


def run_modern_mode():
    """运行现代模式（前后端分离）"""
    import asyncio
    from autohack.main import main

    asyncio.run(main())


if __name__ == "__main__":
    if check_frontend_backend_support():
        try:
            run_modern_mode()
        except Exception as e:
            print(f"Error in modern mode: {e}")
            print("Falling back to legacy mode...")
            run_legacy_mode()
    else:
        run_legacy_mode()
