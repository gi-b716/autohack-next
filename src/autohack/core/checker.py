from autohack.core.constant import *
from autohack.core.exception import *
from autohack.core.path import *
from autohack.core.run import *
from autohack.core.util import *
from typing import Any, Callable, TypeAlias
import importlib.util, subprocess, inspect, pathlib

checkerType: TypeAlias = Callable[[bytes, bytes, bytes, dict], tuple[bool, str]]


def builtinBasicCheckerActivate(args: dict) -> checkerType:
    def builtinBasicChecker(
        input: bytes, output: bytes, answer: bytes, args: dict
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
        input: bytes, output: bytes, answer: bytes, args: dict
    ) -> tuple[bool, str]:
        return (True, "Always AC checker.")

    return builtinAlwaysACChecker


"""
代码	        返回值	含义
_ok	            0	    正确
_wa	            1	    错误
_pe	            2	    格式错误
_fail	        3	    运行失败，程序出错
_dirt	        4	    输出文件含有多余信息
_points	        5	    部分分数
_unexpected_eof	8	    文件读完时仍然尝试读入
_partially	    16+分数	部分正确

from https://www.luogu.com/article/t5rrziq7
"""


def builtinTestlibCheckerActivate(args: dict) -> checkerType:
    ensureDirExists(DATA_FOLDER_PATH / "testlibCheckerCache")
    checkerPath = DATA_FOLDER_PATH / "testlibCheckerCache" / "checker"
    compileCommand = [
        args.get("compiler", "g++"),
        args.get("checker", "checker.cpp"),
        "-o",
        checkerPath.as_posix(),
    ]
    compileCommand += args.get("compile_args", [])
    try:
        compileCode(compileCommand, "checker")
    except CompilationError as e:
        print(e.getMessage())
        raise

    def builtinTestlibChecker(
        input: bytes, output: bytes, answer: bytes, args: dict
    ) -> tuple[bool, str]:
        inputPath = DATA_FOLDER_PATH / "testlibCheckerCache" / "input"
        outputPath = DATA_FOLDER_PATH / "testlibCheckerCache" / "output"
        answerPath = DATA_FOLDER_PATH / "testlibCheckerCache" / "answer"
        resultPath = DATA_FOLDER_PATH / "testlibCheckerCache" / "result"
        checkerPath = DATA_FOLDER_PATH / "testlibCheckerCache" / "checker"
        writeData(inputPath, input)
        writeData(outputPath, output)
        writeData(answerPath, answer)
        command = [
            checkerPath.as_posix(),
            inputPath.as_posix(),
            outputPath.as_posix(),
            answerPath.as_posix(),
            resultPath.as_posix(),
        ]
        result = subprocess.run(
            command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ).returncode
        if not resultPath.exists():
            raise FileNotFoundError("Testlib checker did not produce a result file.")
        resultContent = readData(resultPath).decode().strip()
        if result == 0:
            return (True, f"{resultContent} (Code {result})")
        elif result == 3:
            raise RuntimeError(
                f"Testlib checker runtime error. Checker output: {resultContent}"
            )
        return (False, f"{resultContent} (Code {result})")

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

    if param_types != [bytes, bytes, bytes, dict]:
        raise TypeError(
            f"Checker '{checkerName}' function parameters must be of types (bytes, bytes, dict)."
        )

    if sig.return_annotation != tuple[bool, str]:
        raise TypeError(
            f"Checker '{checkerName}' function must return tuple[bool, str]."
        )

    return checker
