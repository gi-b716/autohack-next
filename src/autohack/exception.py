from . import util
import os


class CompilationError(Exception):
    def __init__(self, fileName: str, message: str, returnCode: int) -> None:
        self.fileName = fileName
        self.message = message
        self.returnCode = returnCode

    def __str__(self) -> str:
        return f"{self.fileName.capitalize()} compilation failed with return code {self.returnCode}\n\n{self.message}"


class DataGenerationError(Exception):
    def __init__(self, data: str, clientID: str, returnCode: int) -> None:
        self.clientID = clientID
        self.returnCode = returnCode
        util.checkDirectoryExists(os.path.dirname(util.getTempInputFilePath(clientID)))
        open(util.getTempInputFilePath(clientID), "w").write(data)

    def __str__(self) -> str:
        return f"Data generation failed with return code {self.returnCode}. Output saved to {util.getTempInputFilePath(self.clientID)}"
