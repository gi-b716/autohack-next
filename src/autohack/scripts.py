def entrypoint() -> None:
    import os

    os.environ["AUTOHACK_ENTRYPOINT"] = "1"
    from . import __main__
