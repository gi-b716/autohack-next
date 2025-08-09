def entrypoint() -> None:
    import os

    os.environ["AUTOHACK_ENTRYPOINT"] = "1"
    from autohack import __main__
