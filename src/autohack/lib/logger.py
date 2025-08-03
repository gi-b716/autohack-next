import logging, time, os


class Logger:
    def __init__(self, logFolder: str, logLevel=logging.WARNING) -> None:
        self.logFolder = logFolder
        self.logLevel = logLevel

        # Create log folder
        if not os.path.isdir(self.logFolder):
            os.mkdir(self.logFolder)

        self.logger = logging.getLogger("autohack")
        self.logger.setLevel(logLevel)
        self.logFilePath = os.path.join(
            self.logFolder,
            f"autohack-{time.strftime("%Y-%m-%d_%H-%M-%S",time.localtime(time.time()))}.log",
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

    def getLogFilePath(self) -> str:
        return self.logFilePath
