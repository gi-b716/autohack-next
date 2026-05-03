class autohackRuntimeError(Exception):
    def __init__(self, output: bytes, returnCode: int) -> None:
        self.output = output
        self.returnCode = returnCode
