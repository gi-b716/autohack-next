"""
Note (2026/4/16):
- Do NOT import `autohack.core.util` directly. Probably circular import.
"""

from .ansi import *
from .console import *
from .fs import *
from .run import *
from .spec import *
from .system import *

__all__ = [
    # .ansi
    "ANSIHelper",
    # .console
    "write",
    "getTranslatedMessage",
    "writeMessage",
    "showCursor",
    "hideCursor",
    "selectionMenu",
    # .fs
    "ensureDirExists",
    "writeData",
    "readData",
    "getFolderSize",
    # .run
    "compileCode",
    "generateInput",
    "generateAnswer",
    "runSourceCode",
    # .spec
    "getFunctionInfo",
    # .system
    "exitProgram",
]
