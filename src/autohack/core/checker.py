from tabnanny import check
from autohack.core.constant import *
from autohack.core.path import *
from autohack.core.util import *
from typing import Any, Callable, TypeAlias
import importlib.util, inspect, pathlib

checkerType: TypeAlias = Callable[[bytes, bytes, dict], tuple[bool, str]]


def builtinBasicCheckerActivate(args: dict) -> checkerType:
    def builtinBasicChecker(
        output: bytes, answer: bytes, args: dict
    ) -> tuple[bool, str]:
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

    return builtinBasicChecker


def builtinAlwaysACCheckerActivate(args: dict) -> checkerType:
    def builtinAlwaysACChecker(
        output: bytes, answer: bytes, args: dict
    ) -> tuple[bool, str]:
        return (True, "Always AC checker.")

    return builtinAlwaysACChecker


def builtinTestlibCheckerActivate(args: dict) -> checkerType:
    def builtinTestlibChecker(
        output: bytes, answer: bytes, args: dict
    ) -> tuple[bool, str]:
        testlibPath = CHECKER_FOLDER_PATH / ".cache" / "testlib.h"
        ensureDirExists(testlibPath.parent)
        if not testlibPath.exists():
            return (False, "testlib.h not found in .cache folder.")
        return (True, "Testlib checker placeholder.")

    return builtinTestlibChecker


BUILTIN = [
    ("builtin_basic", builtinBasicCheckerActivate),
    ("builtin_always_ac", builtinAlwaysACCheckerActivate),
    ("builtin_testlib", builtinTestlibCheckerActivate),
]


"""
Checker 中的 activate 函数签名为 (dict) -> Callable[[bytes, bytes, dict], tuple[bool, str]]
即接受 args 返回 checker 函数
"""


def getChecker(
    checkerFolder: pathlib.Path, checkerName: str, args: dict[str, Any]
) -> checkerType:
    # 如果 checkerName 在 BUILTIN 中，直接返回对应的函数
    for name, func in BUILTIN:
        if name == checkerName:
            return func(args)

    checkerPath = checkerFolder / f"{checkerName}.py"
    if not checkerPath.exists():
        raise FileNotFoundError(f'Checker "{checkerPath}" not found.')

    spec = importlib.util.spec_from_file_location(checkerName, checkerPath)
    if spec is None or spec.loader is None:
        raise ImportError(f'Could not load spec for checker "{checkerName}".')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "activate"):
        raise AttributeError(
            f"Checker '{checkerName}' does not have a 'activate' function."
        )

    try:
        checker = module.activate(args)
    except Exception as e:
        raise RuntimeError(f"Error while activating checker '{checkerName}': {e}")

    sig = inspect.signature(checker)
    params = sig.parameters
    param_types = [param.annotation for param in params.values()]

    if param_types != [bytes, bytes, dict]:
        raise TypeError(
            f"Checker '{checkerName}' function parameters must be of types (bytes, bytes, dict)."
        )

    if sig.return_annotation != tuple[bool, str]:
        raise TypeError(
            f"Checker '{checkerName}' function must return tuple[bool, str]."
        )

    return checker
