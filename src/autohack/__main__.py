from .constant import *
from . import exception, function, config, logger, util
import platform, logging, uuid, os

util.checkDirectoryExists(DATA_FOLDER_PATH)
util.checkDirectoryExists(LOG_FOLDER_PATH)
util.checkDirectoryExists(TEMP_FOLDER_PATH)
if platform.system().lower() == "windows":
    os.system("attrib +h {0}".format(DATA_FOLDER_PATH))

# TODO Remember to delete DEBUG tag
logger = logger.Logger(LOG_FOLDER_PATH, logging.DEBUG).getLogger()
config = config.Config(CONFIG_FILE_PATH, logger)
logger.info(f'[autohack] Data folder path: "{DATA_FOLDER_PATH}"')
clientID = str(uuid.uuid4())
logger.info(f"[autohack] Client ID: {clientID}")
filesPath = FilesPath(clientID)
util.checkDirectoryExists(filesPath.clientFolderPath)
logger.info(f"[autohack] Created client folder: {filesPath.clientFolderPath}")
logger.info("[autohack] Initialized.")


if __name__ == "__main__":
    fileList = [
        [config.getConfigEntry("commands.compile.source"), "source code"],
        [config.getConfigEntry("commands.compile.std"), "standard code"],
        [config.getConfigEntry("commands.compile.checker"), "checker code"],
        [config.getConfigEntry("commands.compile.generator"), "generator code"],
    ]
    for file in fileList:
        try:
            function.compileCode(file[0], file[1])
        except exception.CompilationError as e:
            logger.error(f"[autohack] {e.fileName.capitalize()} compilation failed.")
            print(f"\r{e}")
            exit(1)
        else:
            logger.info(f"[autohack] {file[1].capitalize()} compiled successfully.")
    print("\x1b[1K\rCompile finished.")
