from autohack.core.path import *
import subprocess, threading, psutil, time, os


class CodeRunner:
    class Result:
        def __init__(
            self,
            timeOut: bool,
            memoryOut: bool,
            returnCode: int | None,
            stdout: bytes | None,
            stderr: bytes | None,
        ) -> None:
            self.timeOut = timeOut
            self.memoryOut = memoryOut
            self.returnCode = returnCode
            self.stdout = stdout
            self.stderr = stderr

    def __init__(self):
        self.timeOut = False
        self.memoryOut = False

    def memoryMonitor(
        self, pid: int, timeLimit: float | None, memoryLimit: int | None
    ) -> None:
        try:
            psutilProcess = psutil.Process(pid)
        except psutil.NoSuchProcess:
            # 跑的太他妈快了，没测到
            return
        startTime = psutilProcess.create_time()
        while True:
            try:
                # psutilProcess.cpu_times();
                if timeLimit is not None and time.time() - startTime > timeLimit:
                    self.timeOut = True
                    psutilProcess.kill()
                    return
                # 测出来是资源监视器内存中提交那栏 *1024
                if (
                    memoryLimit is not None
                    and psutilProcess.memory_info().vms > memoryLimit
                ):
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
            monitor = threading.Thread(
                target=self.memoryMonitor,
                args=(
                    process.pid,
                    timeLimit,
                    memoryLimit,
                ),
            )
            monitor.start()
            stdout, stderr = process.communicate(inputContent) # type: ignore
            # try:
            #     stdout, stderr = process.communicate(inputContent, timeout=timeLimit)
            # except subprocess.TimeoutExpired:
            #     process.kill()
            #     if mswindows():
            #         stdout, stderr = process.communicate()
            #     else:
            #         process.wait()
            #     timeOut = True
            returnCode = process.poll()
        return self.Result(self.timeOut, self.memoryOut, returnCode, stdout, stderr) # type: ignore


def checkDirectoryExists(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


def mswindows() -> bool:
    try:
        import msvcrt
    except ModuleNotFoundError:
        return False
    else:
        return True
