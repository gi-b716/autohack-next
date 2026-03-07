import platformdirs, pathlib, time, os

dirs = platformdirs.PlatformDirs("autohack", "Gavin", version="v1")

DATA_FOLDER_PATH = pathlib.Path(os.getcwd()) / ".autohack"

HACK_DATA_STORAGE_FOLDER_PATH = DATA_FOLDER_PATH / "datastorage"

CHECKER_FOLDER_PATH = DATA_FOLDER_PATH / "checkers"

EXPORT_FOLDER_PATH = DATA_FOLDER_PATH / "export"

LOG_FOLDER_PATH = DATA_FOLDER_PATH / "logs"

CONFIG_FILE_PATH = DATA_FOLDER_PATH / "config.json"

GLOBAL_DATA_FOLDER_PATH = pathlib.Path(dirs.user_data_dir)

GLOBAL_CONFIG_FILE_PATH = GLOBAL_DATA_FOLDER_PATH / "config.json"

TRANSLATION_FOLDER_PATH = pathlib.Path(__file__).parent.parent / "assets" / "i18n"


def getHackDataStorageFolderPath(clientID: str, startTime: time.struct_time) -> pathlib.Path:
    dateStr = time.strftime("%Y-%m-%d", startTime)
    timeStr = time.strftime("%H-%M-%S", startTime)
    return HACK_DATA_STORAGE_FOLDER_PATH / dateStr / f"{timeStr}_{clientID}"


def getHackDataFilePath(hackDataStorageFolder: pathlib.Path, dataID: int, filePath: str) -> pathlib.Path:
    return hackDataStorageFolder / filePath.replace("$(id)", str(dataID))


def getExportFolderPath(startTime: time.struct_time, clientID: str | None = None) -> pathlib.Path:
    dateStr = time.strftime("%Y-%m-%d", startTime)
    timeStr = time.strftime("%H-%M-%S", startTime)
    if clientID is None:
        return EXPORT_FOLDER_PATH / dateStr / timeStr
    return EXPORT_FOLDER_PATH / dateStr / f"{timeStr}_{clientID}"


def getExportDataPath(exportFolder: pathlib.Path, filePath: str) -> pathlib.Path:
    return exportFolder / filePath
