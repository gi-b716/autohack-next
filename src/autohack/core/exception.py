class CompilationError(Exception):
    def __init__(self, fileName: str, message: bytes, returnCode: int) -> None:
        self.fileName = fileName
        self.message = message
        self.returnCode = returnCode

    def __str__(self) -> str:
        return f"{self.fileName.capitalize()} compilation failed with return code {self.returnCode}.\n\n{self.message.decode()}"


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
