from . import util
import os


class CompilationError(Exception):
    def __init__(self, fileName: str, message: str, returnCode: int) -> None:
        self.fileName = fileName
        self.message = message
        self.returnCode = returnCode

    def __str__(self) -> str:
        return f"{self.fileName.capitalize()} compilation failed with return code {self.returnCode}.\n\n{self.message}"


class InputGenerationError(Exception):
    def __init__(self, dataInput: str, clientID: str, returnCode: int) -> None:
        self.clientID = clientID
        self.returnCode = returnCode
        util.checkDirectoryExists(os.path.dirname(util.getTempInputFilePath(clientID)))
        open(util.getTempInputFilePath(clientID), "w").write(dataInput)

    def __str__(self) -> str:
        return f"Input generation failed with return code {self.returnCode}. Input saved to {util.getTempInputFilePath(self.clientID)}."


class AnswerGenerationError(Exception):
    def __init__(
        self, dataInput: str, dataAnswer: str, clientID: str, returnCode: int
    ) -> None:
        self.clientID = clientID
        self.returnCode = returnCode
        util.checkDirectoryExists(os.path.dirname(util.getTempInputFilePath(clientID)))
        util.checkDirectoryExists(os.path.dirname(util.getTempAnswerFilePath(clientID)))
        open(util.getTempInputFilePath(clientID), "w").write(dataInput)
        open(util.getTempAnswerFilePath(clientID), "w").write(dataAnswer)

    def __str__(self) -> str:
        return f"Answer generation failed with return code {self.returnCode}. Input saved to {util.getTempInputFilePath(self.clientID)}. Answer saved to {util.getTempAnswerFilePath(self.clientID)}."
