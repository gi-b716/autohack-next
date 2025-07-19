from . import constants, config, logger
import platform, logging, os

if not os.path.isdir(constants.DATA_FOLDER_PATH):
    os.mkdir(constants.DATA_FOLDER_PATH)
    if platform.system().lower() == "windows":
        os.system("attrib +h {0}".format(constants.DATA_FOLDER_PATH))

# TODO Remember to delete DEBUG tag
logger = logger.Logger(
    os.path.join(constants.DATA_FOLDER_PATH, "logs"), logging.DEBUG
).logger
config = config.Config(os.path.join(constants.DATA_FOLDER_PATH, "config.json"), logger)
logger.debug(f"[autoHack] Data folder path: \"{constants.DATA_FOLDER_PATH}\"+")
logger.info("[autoHack] Initialized.")
