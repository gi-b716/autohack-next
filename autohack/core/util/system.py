import sys


def exitProgram(exitCode: int = 0, pure: bool = False) -> None:
    if not pure:
        from .console import showCursor

        showCursor()
    sys.exit(exitCode)
