from . import exception, util
import subprocess


def compileCode(compileCommand: str, fileName: str) -> None:
    print(f"\x1b[1K\rCompile {fileName}.", end="")
    process = subprocess.Popen(
        compileCommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    output = process.communicate()[0]
    if process.returncode != 0:
        raise exception.CompilationError(fileName, output, process.returncode)


def generateInput(generateCommand: str, clientID: str) -> bytes:
    print(f"\x1b[1K\rGenerate input.", end="")
    process = subprocess.Popen(
        generateCommand, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    dataInput = process.communicate()[0]
    if process.returncode != 0:
        raise exception.InputGenerationError(dataInput, clientID, process.returncode)
    return dataInput


def generateAnswer(generateCommand: str, dataInput: bytes, clientID: str) -> bytes:
    print(f"\x1b[1K\rGenerate answer.", end="")
    process = subprocess.Popen(
        generateCommand,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    dataAnswer = process.communicate(dataInput)[0]
    if process.returncode != 0:
        raise exception.AnswerGenerationError(
            dataInput, dataAnswer, clientID, process.returncode
        )
    return dataAnswer


def runSourceCode(
    runCommand: str, dataInput: bytes, timeLimit: int | None, memoryLimit: int | None
) -> util.CodeRunner.Result:
    print(f"\x1b[1K\rRun source code.", end="")
    result = util.CodeRunner().run(
        runCommand,
        inputContent=dataInput,
        timeLimit=timeLimit,
        memoryLimit=memoryLimit,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result
