from autohack.core.util import *
import os


class CompilationError(Exception):
    def __init__(self, fileName: str, message: bytes, returnCode: int) -> None:
        self.fileName = fileName
        self.message = message
        self.returnCode = returnCode

    def __str__(self) -> str:
        return (
            highlightText(
                f"{self.fileName.capitalize()} compilation failed with return code {self.returnCode}."
            )
            + f"\n\n{self.message.decode()}"
        )


class InputGenerationError(Exception):
    def __init__(self, clientID: str, returnCode: int) -> None:
        self.clientID = clientID
        self.returnCode = returnCode

    def __str__(self) -> str:
        return highlightText(
            f"Input generation failed with return code {self.returnCode}."
        )


class AnswerGenerationError(Exception):
    def __init__(self, clientID: str, returnCode: int) -> None:
        self.clientID = clientID
        self.returnCode = returnCode

    def __str__(self) -> str:
        return highlightText(
            f"Answer generation failed with return code {self.returnCode}."
        )
