import platformdirs, os

dirs = platformdirs.PlatformDirs("autohack", "Gavin", version="v1")

DATA_FOLDER_PATH = os.path.join(os.getcwd(), ".autohack")

RECORD_FILE_PATH = os.path.join(DATA_FOLDER_PATH, "record.txt")

# LOG_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, "logs")
LOG_FOLDER_PATH = dirs.user_log_dir

TEMP_FOLDER_PATH = dirs.user_runtime_dir

CONFIG_FILE_PATH = os.path.join(DATA_FOLDER_PATH, "config.json")

CURRENT_HACK_DATA_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, "hackdata")

HACK_DATA_STORAGE_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, "datastorage")
