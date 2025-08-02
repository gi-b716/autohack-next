from .i18n import _
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

        self.logger.info(_('Log file: "{0}"').format(logFilePath))
        self.logger.info(_("Log level: {0}").format(logging.getLevelName(logLevel)))
        self.logger.info(_("Logger initialized."))

    def getLogger(self) -> logging.Logger:
        return self.logger
