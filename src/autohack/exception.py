class CompilationError(Exception):
    def __init__(self, fileName: str, message: str) -> None:
        self.fileName = fileName
        self.message = message

    def __str__(self) -> str:
        return f"{self.fileName.capitalize()} compilation failed.\n\n{self.message}"
