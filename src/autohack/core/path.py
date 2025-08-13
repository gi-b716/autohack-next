import platformdirs, os

dirs = platformdirs.PlatformDirs("autohack", "Gavin", version="v1")

DATA_FOLDER_PATH = os.path.join(os.getcwd(), ".autohack")

RECORD_FILE_PATH = os.path.join(DATA_FOLDER_PATH, "record.txt")

LOG_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, "logs")
# LOG_FOLDER_PATH = dirs.user_log_dir

TEMP_FOLDER_PATH = dirs.user_runtime_dir

CONFIG_FILE_PATH = os.path.join(DATA_FOLDER_PATH, "config.json")

CURRENT_HACK_DATA_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, "hackdata")

HACK_DATA_STORAGE_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, "datastorage")


def getTempInputFilePath(clientID: str) -> str:
    return os.path.join(TEMP_FOLDER_PATH, clientID, "input")


def getTempAnswerFilePath(clientID: str) -> str:
    return os.path.join(TEMP_FOLDER_PATH, clientID, "answer")


def getHackDataStorageFolderPath(clientID: str) -> str:
    return os.path.join(HACK_DATA_STORAGE_FOLDER_PATH, clientID)


def getHackDataFilePath(dataID: int, filePath: str) -> str:
    return os.path.join(
        CURRENT_HACK_DATA_FOLDER_PATH, filePath.replace("$(id)", str(dataID))
    )


def getHackDataFolderPath(dataID: int, filePath: str) -> str:
    return os.path.dirname(getHackDataFilePath(dataID, filePath))
