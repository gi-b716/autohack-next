from autohack.core.exception import *
import subprocess, threading, psutil, time


class CodeRunner:
    class Result:
        def __init__(
            self,
            totalTime: float | None,
            timeOut: bool,
            maxMemory: int | None,
            memoryOut: bool,
            returnCode: int | None,
            stdout: bytes | None,
            stderr: bytes | None,
        ) -> None:
            self.totalTime = totalTime
            self.timeOut = timeOut
            self.maxMemory = maxMemory
            self.memoryOut = memoryOut
            self.returnCode = returnCode
            self.stdout = stdout
            self.stderr = stderr

    def __init__(self):
        self.totalTime = None
        self.timeOut = False
        self.maxMemory = None
        self.memoryOut = False

    def memoryMonitor(self, pid: int, timeLimit: float | None, memoryLimit: int | None) -> None:
        try:
            psutilProcess = psutil.Process(pid)
            startTime = psutilProcess.create_time()
            while True:
                # psutilProcess.cpu_times();
                self.totalTime = time.time() - startTime
                if timeLimit is not None and self.totalTime > timeLimit:
                    self.timeOut = True
                    psutilProcess.kill()
                    return
                # 测出来是资源监视器内存中提交那栏 *1024
                self.maxMemory = max(self.maxMemory, psutilProcess.memory_info().vms)
                if memoryLimit is not None and self.maxMemory > memoryLimit:
                    self.memoryOut = True
                    psutilProcess.kill()
                    return
        except psutil.NoSuchProcess:
            return

    def run(
        self,
        *popenargs,
        inputContent: bytes | None = None,
        timeLimit: float | None = None,
        memoryLimit: int | None = None,
        **kwargs,
    ) -> Result:
        returnCode = 0
        stdout = None
        stderr = None
        with subprocess.Popen(*popenargs, **kwargs) as process:
            monitor = threading.Thread(target=self.memoryMonitor, args=(process.pid, timeLimit, memoryLimit))
            monitor.start()
            stdout, stderr = process.communicate(inputContent)  # type: ignore
            returnCode = process.poll()
        return self.Result(self.totalTime, self.timeOut, self.maxMemory, self.memoryOut, returnCode, stdout, stderr)  # type: ignore


def compileCode(compileCommand: list) -> None:
    try:
        process = subprocess.Popen(compileCommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError:
        return
    output = process.communicate()[0]
    if process.returncode != 0:
        raise autohackRuntimeError(output, process.returncode)


def generateInput(generateCommand: list) -> bytes:
    try:
        process = subprocess.Popen(generateCommand, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except OSError:
        return b""
    dataInput = process.communicate()[0]
    if process.returncode != 0:
        raise autohackRuntimeError(dataInput, process.returncode)
    return dataInput


def generateAnswer(generateCommand: list, dataInput: bytes) -> bytes:
    try:
        process = subprocess.Popen(generateCommand, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except OSError:
        return b""
    dataAnswer = process.communicate(dataInput)[0]
    if process.returncode != 0:
        raise autohackRuntimeError(dataAnswer, process.returncode)
    return dataAnswer


def runSourceCode(runCommand: list, dataInput: bytes, timeLimit: float | None, memoryLimit: int | None) -> CodeRunner.Result:
    try:
        result = CodeRunner().run(
            runCommand,
            inputContent=dataInput,
            timeLimit=timeLimit,
            memoryLimit=memoryLimit,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return CodeRunner.Result(None, False, None, False, 0, b"", b"")
    return result
