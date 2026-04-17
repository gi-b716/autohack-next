import pathlib, tarfile, time

from loguru import logger as baseLogger

from autohack.core.util.fs import ensureDirExists


class Logger:
    def __init__(
        self,
        logFolder: pathlib.Path,
        debug: bool = False,
    ) -> None:
        self.logFolder = logFolder
        self.debug = debug
        self.logLevel = "DEBUG" if debug else "INFO"

        ensureDirExists(self.logFolder)

        self.logFilePath = self.logFolder / "latest.log"

        if self.logFilePath.exists():
            try:
                mtime = time.localtime(self.logFilePath.stat().st_mtime)
                dataStr = time.strftime("%Y-%m-%d", mtime)
                idx = 1
                while True:
                    archiveName = self.logFolder / f"{dataStr}-{idx}.log.tar.gz"
                    if not archiveName.exists():
                        break
                    idx += 1

                with tarfile.open(archiveName, "w:gz") as tarf:
                    tarf.add(self.logFilePath, arcname=f"{dataStr}-{idx}.log")
                self.logFilePath.unlink()
            except Exception:
                pass

        baseLogger.remove()

        logFormat = "{time:YYYY-MM-DD HH:mm:ss} | {level} | [{extra[module]}] {message}"
        baseLogger.add(str(self.logFilePath), format=logFormat, level=self.logLevel, encoding="utf-8")

        self.logger = self.getBindLogger("logger")

        self.logger.info(f'Log file: "{self.logFilePath}"')
        self.logger.info(f"Log level: {self.logLevel}")
        self.logger.info("Logger initialized.")

    @staticmethod
    def getBindLogger(name: str):
        return baseLogger.bind(module=name)

    def getLogFilePath(self) -> pathlib.Path:
        return self.logFilePath
