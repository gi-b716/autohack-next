from . import util
import os


class CompilationError(Exception):
    def __init__(self, fileName: str, message: bytes, returnCode: int) -> None:
        self.fileName = fileName
        self.message = message
        self.returnCode = returnCode

    def __str__(self) -> str:
        return f"{self.fileName.capitalize()} compilation failed with return code {self.returnCode}.\n\n{self.message.decode()}"


class InputGenerationError(Exception):
    def __init__(self, dataInput: bytes, clientID: str, returnCode: int) -> None:
        self.clientID = clientID
        self.returnCode = returnCode
        util.checkDirectoryExists(os.path.dirname(util.getTempInputFilePath(clientID)))
        open(util.getTempInputFilePath(clientID), "wb").write(dataInput)

    def __str__(self) -> str:
        return f"Input generation failed with return code {self.returnCode}. Input saved to {util.getTempInputFilePath(self.clientID)}."


class AnswerGenerationError(Exception):
    def __init__(
        self, dataInput: bytes, dataAnswer: bytes, clientID: str, returnCode: int
    ) -> None:
        self.clientID = clientID
        self.returnCode = returnCode
        util.checkDirectoryExists(os.path.dirname(util.getTempInputFilePath(clientID)))
        util.checkDirectoryExists(os.path.dirname(util.getTempAnswerFilePath(clientID)))
        open(util.getTempInputFilePath(clientID), "wb").write(dataInput)
        open(util.getTempAnswerFilePath(clientID), "wb").write(dataAnswer)

    def __str__(self) -> str:
        return f"Answer generation failed with return code {self.returnCode}. Input saved to {util.getTempInputFilePath(self.clientID)}. Answer saved to {util.getTempAnswerFilePath(self.clientID)}."
