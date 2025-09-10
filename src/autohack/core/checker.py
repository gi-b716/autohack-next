from autohack.core.constant import *
from autohack.core.util import *
from typing import Callable
import pathlib

from autohack.core.path import CHECKER_FOLDER_PATH


def builtinBasicChecker(output: bytes, answer: bytes, args: list) -> tuple[bool, str]:
    outputStr = output.decode().rstrip("\n")
    answerStr = answer.decode().rstrip("\n")
    outputLines = outputStr.splitlines()
    answerLines = answerStr.splitlines()
    if len(outputLines) != len(answerLines):
        return (False, "Output and answer have different number of lines.")
    for i in range(len(outputLines)):
        if outputLines[i].rstrip() != answerLines[i].rstrip():
            return (False, f"Line {i + 1} does not match.")
    return (True, "Output matches the answer.")


def builtinAlwaysACChecker(
    output: bytes, answer: bytes, args: list
) -> tuple[bool, str]:
    return (True, "Always AC checker.")


def builtinTestlibChecker(output: bytes, answer: bytes, args: list) -> tuple[bool, str]:
    testlibPath = CHECKER_FOLDER_PATH / ".cache" / "testlib.h"
    ensureDirExists(testlibPath.parent)
    if not testlibPath.exists():
        return (False, "testlib.h not found in .cache folder.")
    return (True, "Testlib checker placeholder.")


BUILTIN = [
    ("builtin_basic", builtinBasicChecker),
    ("builtin_always_ac", builtinAlwaysACChecker),
    ("builtin_testlib", builtinTestlibChecker),
]


def getChecker(
    checkerFolder: pathlib.Path, checkerName: str
) -> Callable[[bytes, bytes, list], tuple[bool, str]]:
    # 如果 checkerName 在 BUILTIN 中，直接返回对应的函数
    for name, func in BUILTIN:
        if name == checkerName:
            return func

    checkerPath = checkerFolder / f"{checkerName}.py"
    if not checkerPath.exists():
        raise FileNotFoundError(f'Checker "{checkerPath}" not found.')
    import importlib.util

    spec = importlib.util.spec_from_file_location(checkerName, checkerPath)
    if spec is None or spec.loader is None:
        raise ImportError(f'Could not load spec for checker "{checkerName}".')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "check"):
        raise AttributeError(
            f"Checker '{checkerName}' does not have a 'check' function."
        )
    # 检查 check 函数的签名是否为 (bytes, bytes, list) -> tuple[bool, str]
    import inspect

    sig = inspect.signature(module.check)
    params = sig.parameters
    if len(params) != 3:
        raise TypeError(
            f"Checker '{checkerName}' check function must have 3 parameters."
        )
    param_types = [param.annotation for param in params.values()]
    if param_types != [bytes, bytes, list]:
        raise TypeError(
            f"Checker '{checkerName}' check function parameters must be of types (bytes, bytes, list)."
        )
    if sig.return_annotation != tuple[bool, str]:
        raise TypeError(
            f"Checker '{checkerName}' check function must return tuple[bool, str]."
        )

    return module.check
