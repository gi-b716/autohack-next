from autohack.lib.i18n import *
from typing import Callable
import inspect, pathlib, shutil, time, sys, os


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


def readData(filePath: pathlib.Path) -> bytes:
    return open(filePath, "rb").read()


def clearLine() -> None:
    write("\x1b[2K\r")


def prevLine() -> None:
    write("\x1b[1A")


def outputEndl(count: int = 1) -> None:
    sys.stdout.write("\n" * count)


def inputMessage(prompt: str = "", endl: int = 0, clear: bool = False) -> str:
    showCursor()
    write(prompt, endl, clear)
    try:
        return input()
    finally:
        hideCursor()


def write(message: str, endl: int = 0, clear: bool = False, highlight: bool = False) -> None:
    if clear:
        clearLine()
    if highlight:
        message = highlightText(message)
    sys.stdout.write(message)
    outputEndl(endl)
    sys.stdout.flush()


def getTranslatedMessage(I18n: I18N, message: str, *args, language: str = "") -> str:
    return I18n.translate(message, language).format(*map(str, args))


def writeMessage(
    I18n: I18N,
    message: str,
    *args,
    language: str = "",
    endl: int = 0,
    clear: bool = False,
    highlight: bool = False,
) -> None:
    write(I18n.translate(message, language).format(*map(str, args)), endl, clear, highlight)


def hideCursor() -> None:
    # https://www.cnblogs.com/chargedcreeper/p/-/ANSI
    write("\x1b[?25l")


def showCursor() -> None:
    write("\x1b[?25h")


def highlightText(message: str) -> str:
    return f"\x1b[1;31m{message}\x1b[0m"


def exitProgram(exitCode: int = 0, pure: bool = False) -> None:
    if not pure:
        showCursor()
    sys.exit(exitCode)


def getFunctionInfo(func: Callable) -> tuple[list[type], type]:
    sig = inspect.signature(func)
    params = sig.parameters
    paramTypes = [param.annotation for param in params.values()]
    return (paramTypes, sig.return_annotation)


def getFolderSize(folderPath: pathlib.Path) -> int:
    # return shutil.disk_usage(folderPath).used
    totalSize = 0
    with os.scandir(folderPath) as entries:
        for entry in entries:
            if entry.is_file():
                totalSize += entry.stat().st_size
            elif entry.is_dir():
                totalSize += getFolderSize(pathlib.Path(entry.path))
    return totalSize
