import pathlib, time, sys, os


def ensureDirExists(dirPath: pathlib.Path) -> None:
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)


def mswindows() -> bool:
    try:
        import msvcrt
    except ModuleNotFoundError:
        return False
    else:
        return True


def formatTime(t: time.struct_time = time.localtime()) -> str:
    return time.strftime("%Y%m%d%H%M%S", t)


def writeData(filePath: pathlib.Path, data: bytes) -> None:
    ensureDirExists(filePath.parent)
    open(filePath, "wb").write(data)


def clearLine() -> None:
    write("\x1b[2K\r")


def prevLine() -> None:
    write("\x1b[1A")


def outputEndl(count: int = 1) -> None:
    sys.stdout.write("\n" * count)


def write(message: str, endl: int = 0, clear: bool = False) -> None:
    if clear:
        clearLine()
    sys.stdout.write(message)
    outputEndl(endl)
    sys.stdout.flush()


def hideCursor() -> None:
    # https://www.cnblogs.com/chargedcreeper/p/-/ANSI
    write("\x1b[?25l")


def showCursor() -> None:
    write("\x1b[?25h")


def highlightText(message: str) -> str:
    return f"\x1b[1;31m{message}\x1b[0m"


def exitProgram(exitCode: int = 0) -> None:
    showCursor()
    sys.exit(exitCode)
