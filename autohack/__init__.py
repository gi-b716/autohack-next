__VERSION__ = "1.1.0.dev5"


def entrypoint():
    from argparse import ArgumentParser
    import uuid, time
    import colorama
    from autohack.central import AppCentral

    colorama.just_fix_windows_console()

    argsParser = ArgumentParser(
        prog="autohack",
        description="autohack-next - Automated hack data generator",
    )
    argsParser.add_argument("--version", "-v", action="version", version=__VERSION__)

    args = argsParser.parse_args()

    app = AppCentral(str(uuid.uuid4()), time.localtime(), debug=False)
    app.run()

    # TODO: Keyboard interrupt handling
