import platformdirs, pathlib, os

dirs = platformdirs.PlatformDirs("autohack", "Gavin", version="v1")

DATA_FOLDER_PATH = pathlib.Path(os.getcwd()) / ".autohack"

HACK_DATA_STORAGE_FOLDER_PATH = DATA_FOLDER_PATH / "datastorage"

LOG_FOLDER_PATH = DATA_FOLDER_PATH / "logs"

CONFIG_FILE_PATH = DATA_FOLDER_PATH / "config.json"

GLOBAL_DATA_FOLDER_PATH = pathlib.Path(dirs.user_data_dir)

GLOBAL_CONFIG_FILE_PATH = GLOBAL_DATA_FOLDER_PATH / "config.json"

TRANSLATION_FOLDER_PATH = pathlib.Path(__file__).parent.parent / "i18n"


def getHackDataStorageFolderPath(clientID: str) -> pathlib.Path:
    return HACK_DATA_STORAGE_FOLDER_PATH / clientID


def getHackDataFilePath(dataID: int, filePath: str) -> pathlib.Path:
    return HACK_DATA_STORAGE_FOLDER_PATH / filePath.replace("$(id)", str(dataID))
