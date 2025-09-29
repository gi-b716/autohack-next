from autohack.core.constant import *


class autohackCompilationError(Exception):
    def __init__(self, fileName: str, output: bytes, returnCode: int) -> None:
        self.fileName = fileName
        self.output = output
        self.returnCode = returnCode


class InputGenerationError(Exception):
    def __init__(self, clientID: str, returnCode: int) -> None:
        self.clientID = clientID
        self.returnCode = returnCode

    def __str__(self) -> str:
        return f"Input generation failed with return code {self.returnCode}."


class AnswerGenerationError(Exception):
    def __init__(self, clientID: str, returnCode: int) -> None:
        self.clientID = clientID
        self.returnCode = returnCode

    def __str__(self) -> str:
        return f"Answer generation failed with return code {self.returnCode}."
