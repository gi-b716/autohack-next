from autohack.core.util import *
import os


class CompilationError(Exception):
    def __init__(self, fileName: str, message: bytes, returnCode: int) -> None:
        self.fileName = fileName
        self.message = message
        self.returnCode = returnCode

    def __str__(self) -> str:
        return f"\x1b[1;31m{self.fileName.capitalize()} compilation failed with return code {self.returnCode}.\x1b[0m\n\n{self.message.decode()}"


class InputGenerationError(Exception):
    def __init__(self, dataInput: bytes, clientID: str, returnCode: int) -> None:
        self.clientID = clientID
        self.returnCode = returnCode
        checkDirectoryExists(os.path.dirname(getTempInputFilePath(clientID)))
        open(getTempInputFilePath(clientID), "wb").write(dataInput)

    def __str__(self) -> str:
        return f"\x1b[1;31mInput generation failed with return code {self.returnCode}. Input saved to {getTempInputFilePath(self.clientID)}.\x1b[0m"


class AnswerGenerationError(Exception):
    def __init__(
        self, dataInput: bytes, dataAnswer: bytes, clientID: str, returnCode: int
    ) -> None:
        self.clientID = clientID
        self.returnCode = returnCode
        checkDirectoryExists(os.path.dirname(getTempInputFilePath(clientID)))
        checkDirectoryExists(os.path.dirname(getTempAnswerFilePath(clientID)))
        open(getTempInputFilePath(clientID), "wb").write(dataInput)
        open(getTempAnswerFilePath(clientID), "wb").write(dataAnswer)

    def __str__(self) -> str:
        return f"\x1b[1;31mAnswer generation failed with return code {self.returnCode}. Input saved to {getTempInputFilePath(self.clientID)}. Answer saved to {getTempAnswerFilePath(self.clientID)}.\x1b[0m"
