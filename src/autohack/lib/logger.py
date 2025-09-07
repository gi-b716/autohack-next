from autohack.core.util import *
import logging, pathlib, time, os


class Logger:
    def __init__(
        self, logFolder: pathlib.Path, logLevel: int = logging.WARNING
    ) -> None:
        self.logFolder = logFolder
        self.logLevel = logLevel

        ensureDirExists(self.logFolder)

        self.logger = logging.getLogger("autohack")
        self.logger.setLevel(logLevel)

        self.logFilePath = (
            self.logFolder
            / f"autohack-{time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))}.log"
        )

        logFile = logging.FileHandler(self.logFilePath, encoding="utf-8")
        logFile.setLevel(logLevel)
        logFile.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
        )

        self.logger.addHandler(logFile)

        self.logger.info(f'[logger] Log file: "{self.logFilePath}"')
        self.logger.info(f"[logger] Log level: {logging.getLevelName(logLevel)}")
        self.logger.info("[logger] Logger initialized.")

    def getLogger(self) -> logging.Logger:
        return self.logger

    def getLogFilePath(self) -> pathlib.Path:
        return self.logFilePath
