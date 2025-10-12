from autohack.lib.i18n import *
from typing import Callable
import readchar, inspect, pathlib, time, sys, os


def ensureDirExists(dirPath: pathlib.Path) -> None:
    dirPath.mkdir(parents=True, exist_ok=True)


def mswindows() -> bool:
    # Trick from subprocess
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


def selectionMenu(selectionList: list[str]) -> int:
    currentSelection = 0
    write("Use Up/Down arrows to navigate, Enter to select.", 1)

    def updateSelection() -> None:
        for i, selectionItem in enumerate(selectionList):
            write(
                f"{">" if i == currentSelection else " "} {selectionItem}",
                1 if i < len(selectionList) - 1 else 0,
                clear=True,
                highlight=(i == currentSelection),
            )

    while True:
        updateSelection()
        k = readchar.readkey()
        if k == readchar.key.UP or k == "k":
            currentSelection = currentSelection - 1 if currentSelection > 0 else len(selectionList) - 1
        elif k == readchar.key.DOWN or k == "j":
            currentSelection = currentSelection + 1 if currentSelection < len(selectionList) - 1 else 0
        elif k == readchar.key.ENTER:
            for _ in range(len(selectionList) + 1):
                clearLine()
                prevLine()
            return currentSelection
        elif k == readchar.key.ESC:
            exitProgram(0)
        for _ in range(len(selectionList) - 1):
            prevLine()
