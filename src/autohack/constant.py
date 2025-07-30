import platformdirs, os

dirs = platformdirs.PlatformDirs("autohack", "Gavin", version="v1")

DATA_FOLDER_PATH = os.path.join(os.getcwd(), ".autohack")

# LOG_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, "logs")
LOG_FOLDER_PATH = dirs.user_log_dir

TEMP_FOLDER_PATH = dirs.user_runtime_dir

CONFIG_FILE_PATH = os.path.join(DATA_FOLDER_PATH, "config.json")


class FilesPath:
    def __init__(self, clientID: str) -> None:
        self.clientFolderPath = os.path.join(TEMP_FOLDER_PATH, clientID)
        self.inputFilePath = os.path.join(self.clientFolderPath, "input")
        self.outputFilePath = os.path.join(self.clientFolderPath, "output")
        self.answerFilePath = os.path.join(self.clientFolderPath, "answer")
