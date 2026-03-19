# https://www.cnblogs.com/chargedcreeper/p/-/ANSI


class ANSIHelper:
    CLEAR_LINE = "\x1b[2K\r"
    PREV_LINE = "\x1b[1A"
    NEXT_LINE = "\n"

    HIDE_CURSOR = "\x1b[?25l"
    SHOW_CURSOR = "\x1b[?25h"

    TEMPLATE = "\x1b[{}m"

    RESET = "0"
    BOLD = "1"
    DIM = "2"
    ITALIC = "3"
    UNDERLINE = "4"
    REVERSED = "7"
    DELETELINE = "9"

    BLACK = "30"
    RED = "31"
    GREEN = "32"
    YELLOW = "33"
    BLUE = "34"
    MAGENTA = "35"
    CYAN = "36"
    WHITE = "37"

    @staticmethod
    def formatCode(effect: list[str]) -> str:
        return ANSIHelper.TEMPLATE.format(";".join(effect))

    @staticmethod
    def colorText(text: str, effect: str | list[str] | None) -> str:
        effect = [effect] if isinstance(effect, str) else (effect or [])
        return f"{ANSIHelper.formatCode(effect)}{text}{ANSIHelper.formatCode([ANSIHelper.RESET])}"

    @staticmethod
    def clearLine() -> str:
        return ANSIHelper.CLEAR_LINE

    @staticmethod
    def prevLine(count: int = 1) -> str:
        return ANSIHelper.PREV_LINE * max(0, count)

    @staticmethod
    def nextLine(count: int = 1) -> str:
        return ANSIHelper.NEXT_LINE * max(0, count)

    @staticmethod
    def hideCursor() -> str:
        return ANSIHelper.HIDE_CURSOR

    @staticmethod
    def showCursor() -> str:
        return ANSIHelper.SHOW_CURSOR
