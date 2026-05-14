import sys

import readchar

from .ansi import ANSIHelper


def write(
    *messages: str,
    endl: int = 0,
    sep: str = "",
    clear: bool = False,
    flush: bool = True,
) -> None:
    if clear:
        sys.stdout.write(ANSIHelper.CLEAR_LINE)
    message = sep.join(messages)
    sys.stdout.write(message)
    sys.stdout.write("\n" * endl)
    if flush:
        sys.stdout.flush()


def writeMessage(
    message: str,
    *args,
    endl: int = 0,
    clear: bool = False,
    highlight: bool = False,
) -> None:
    if args:
        message = message.format(*map(str, args))
    if highlight:
        message = ANSIHelper.colorText(message, [ANSIHelper.BOLD, ANSIHelper.RED])
    write(message, endl=endl, clear=clear)


def showCursor() -> None:
    write(ANSIHelper.showCursor())


def hideCursor() -> None:
    write(ANSIHelper.hideCursor())


def selectionMenu(selectionList: list[str]) -> int:
    from .system import exitProgram

    currentSelection = 0
    write("Use Up/Down arrows to navigate, Enter to select.", endl=1)

    def updateSelection() -> None:
        for i, selectionItem in enumerate(selectionList):
            write(
                ANSIHelper.colorText(
                    f"{'>' if i == currentSelection else ' '} {selectionItem}",
                    [ANSIHelper.RED, ANSIHelper.BOLD] if i == currentSelection else [],
                ),
                endl=1 if i < len(selectionList) - 1 else 0,
                clear=True,
                # highlight=(i == currentSelection),
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
                write(ANSIHelper.CLEAR_LINE)
                write(ANSIHelper.PREV_LINE)
            return currentSelection
        elif k == readchar.key.ESC:
            exitProgram(0)
        for _ in range(len(selectionList) - 1):
            write(ANSIHelper.PREV_LINE)
