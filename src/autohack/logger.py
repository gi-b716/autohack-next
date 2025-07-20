import logging, time, os


class Logger:
    def __init__(self, logFolder: str, logLevel=logging.INFO) -> None:
        self.logFolder = logFolder
        self.logLevel = logLevel

        # Create log folder
        if not os.path.isdir(self.logFolder):
            os.mkdir(self.logFolder)

        self.logger = logging.getLogger("autohack")
        self.logger.setLevel(logLevel)
        logFilePath = os.path.join(
            self.logFolder,
            f"autohack-{time.strftime("%Y-%m-%d_%H-%M-%S",time.localtime(time.time()))}.log",
        )
        logFile = logging.FileHandler(logFilePath, encoding="utf-8")
        logFile.setLevel(logLevel)
        logFile.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
        )
        self.logger.addHandler(logFile)

        self.logger.debug(f'[logger] Log file: "{logFilePath}"')
        self.logger.debug(f"[logger] Log level: {logging.getLevelName(logLevel)}")
        self.logger.info("[logger] Logger initialized.")
