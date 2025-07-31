from . import exception
import subprocess


def compileCode(compileCommand: str, fileName: str) -> None:
    print(f"\x1b[1K\rCompile {fileName}.", end="")
    process = subprocess.Popen(
        compileCommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    output = process.communicate()[0]
    if process.returncode != 0:
        raise exception.CompilationError(fileName, output, process.returncode)


def generateInput(generateCommand: str, clientID: str) -> str:
    print(f"\x1b[1K\rGenerate input.", end="")
    process = subprocess.Popen(
        generateCommand, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )
    dataInput = process.communicate()[0]
    if process.returncode != 0:
        raise exception.InputGenerationError(dataInput, clientID, process.returncode)
    return dataInput


def generateAnswer(generateCommand: str, dataInput: str, clientID: str) -> str:
    print(f"\x1b[1K\rGenerate answer.", end="")
    process = subprocess.Popen(
        generateCommand,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    dataAnswer = process.communicate(dataInput)[0]
    if process.returncode != 0:
        raise exception.AnswerGenerationError(
            dataInput, dataAnswer, clientID, process.returncode
        )
    return dataAnswer
