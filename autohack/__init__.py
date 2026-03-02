__VERSION__ = None
try:
    from importlib.metadata import version

    __VERSION__ = version("autohack-next")
except Exception:
    pass


def entrypoint():
    from argparse import ArgumentParser
    import secrets, time
    import colorama
    from autohack.central import AppCentral

    colorama.just_fix_windows_console()

    argsParser = ArgumentParser(
        prog="autohack",
        description="autohack-next - Automated hack data generator",
    )
    argsParser.add_argument("--version", "-v", action="version", version=__VERSION__)
    argsParser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode", default=False)

    args = argsParser.parse_args()

    # 使用 8位 短随机字符代替过长的 UUID，防止冗长同时保证多个实例独立
    app = AppCentral(secrets.token_hex(4), time.localtime(), debug=args.debug)
    app.run()

    # TODO: Keyboard interrupt handling
