def entrypoint() -> None:
    """智能入口点，自动选择最佳运行模式"""
    try:
        # 尝试检查依赖
        import fastapi
        import uvicorn
        import websockets

        # 如果依赖可用，使用前后端分离模式
        import asyncio
        from autohack.main import main

        asyncio.run(main())

    except ImportError:
        # 依赖不可用，使用传统模式
        print(
            "Warning: Running in legacy mode (frontend-backend dependencies not available)"
        )
        print("For better performance, install: pip install fastapi uvicorn websockets")
        print()
        legacy_entrypoint()
    except Exception as e:
        # 如果新模式出错，回退到传统模式
        print(f"Error in frontend-backend mode: {e}")
        print("Falling back to legacy mode...")
        legacy_entrypoint()


def legacy_entrypoint() -> None:
    """旧版入口点，保持兼容性"""
    import os

    os.environ["AUTOHACK_ENTRYPOINT"] = "1"
    from autohack import __main__
