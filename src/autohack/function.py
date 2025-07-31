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


def generateData(generateCommand: str, clientID: str) -> str:
    print(f"\x1b[1K\rGenerate data.", end="")
    process = subprocess.Popen(
        generateCommand, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )
    output = process.communicate()[0]
    if process.returncode != 0:
        raise exception.DataGenerationError(output, clientID, process.returncode)
    return output
