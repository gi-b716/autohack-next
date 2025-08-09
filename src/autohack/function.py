from autohack.core.exception import *
from autohack.core.util import *
import subprocess


def compileCode(compileCommand: str, fileName: str) -> None:
    try:
        process = subprocess.Popen(
            compileCommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
    except OSError:
        return
    output = process.communicate()[0]
    if process.returncode != 0:
        raise CompilationError(fileName, output, process.returncode)


def generateInput(generateCommand: str, clientID: str) -> bytes:
    try:
        process = subprocess.Popen(
            generateCommand, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
    except OSError:
        return b""
    dataInput = process.communicate()[0]
    if process.returncode != 0:
        raise InputGenerationError(dataInput, clientID, process.returncode)
    return dataInput


def generateAnswer(generateCommand: str, dataInput: bytes, clientID: str) -> bytes:
    try:
        process = subprocess.Popen(
            generateCommand,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return b""
    dataAnswer = process.communicate(dataInput)[0]
    if process.returncode != 0:
        raise AnswerGenerationError(dataInput, dataAnswer, clientID, process.returncode)
    return dataAnswer


def runSourceCode(
    runCommand: str, dataInput: bytes, timeLimit: int | None, memoryLimit: int | None
) -> CodeRunner.Result:
    try:
        result = CodeRunner().run(
            runCommand,
            inputContent=dataInput,
            timeLimit=timeLimit,
            memoryLimit=memoryLimit,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return CodeRunner.Result(False, False, 0, b"", b"")
    return result
