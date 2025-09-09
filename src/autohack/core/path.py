from autohack.core.util import *
import platformdirs, pathlib, time, os

dirs = platformdirs.PlatformDirs("autohack", "Gavin", version="v1")

DATA_FOLDER_PATH = pathlib.Path(os.getcwd()) / ".autohack"

HACK_DATA_STORAGE_FOLDER_PATH = DATA_FOLDER_PATH / "datastorage"

EXPORT_FOLDER_PATH = DATA_FOLDER_PATH / "export"

LOG_FOLDER_PATH = DATA_FOLDER_PATH / "logs"

CONFIG_FILE_PATH = DATA_FOLDER_PATH / "config.json"

GLOBAL_DATA_FOLDER_PATH = pathlib.Path(dirs.user_data_dir)

GLOBAL_CONFIG_FILE_PATH = GLOBAL_DATA_FOLDER_PATH / "config.json"

TRANSLATION_FOLDER_PATH = pathlib.Path(__file__).parent.parent / "i18n"


def getHackDataStorageFolderPath(
    clientID: str, startTime: time.struct_time
) -> pathlib.Path:
    return HACK_DATA_STORAGE_FOLDER_PATH / f"{formatTime(startTime)}_{clientID}"


def getHackDataFilePath(
    hackDataStorageFolder: pathlib.Path, dataID: int, filePath: str
) -> pathlib.Path:
    return hackDataStorageFolder / filePath.replace("$(id)", str(dataID))


def getExportFolderPath(
    startTime: time.struct_time, clientID: str | None = None
) -> pathlib.Path:
    if clientID is None:
        return EXPORT_FOLDER_PATH / formatTime(startTime)
    return EXPORT_FOLDER_PATH / f"{formatTime(startTime)}_{clientID}"


def getExportDataPath(exportFolder: pathlib.Path, filePath: str) -> pathlib.Path:
    return exportFolder / filePath
