from .constants import *
from .config import Config
from .logger import Logger
import subprocess, platform, logging, os

if not os.path.isdir(DATA_FOLDER_PATH):
    os.mkdir(DATA_FOLDER_PATH)
    if platform.system().lower() == "windows":
        os.system("attrib +h {0}".format(DATA_FOLDER_PATH))

# TODO Remember to delete DEBUG tag
logger = Logger(LOG_FOLDER_PATH, logging.DEBUG).logger
config = Config(CONFIG_FILE_PATH, logger)
logger.debug(f'[autoHack] Data folder path: "{DATA_FOLDER_PATH}"')
logger.info("[autoHack] Initialized.")


def compileCode() -> None:
    """
    Compile the source code using the commands specified in the config file.
    """
    print("Compiling source code.")
    logger.info("[autoHack] Compiling source code.")
    logger.debug(
        f"[autoHack] Compile command: {config.getConfigEntry('commands.compile.source')}"
    )
    process = subprocess.Popen(config.getConfigEntry("commands.compile.source"))
    process.communicate()
    if process.returncode != 0:
        logger.error("[autoHack] Compilation failed.")
        raise RuntimeError("Compilation failed.")
    logger.info("[autoHack] Source code compiled successfully.")

    print("Compiling standard code.")
    logger.info("[autoHack] Compiling standard code.")
    logger.debug(
        f"[autoHack] Compile command: {config.getConfigEntry('commands.compile.std')}"
    )
    process = subprocess.Popen(config.getConfigEntry("commands.compile.std"))
    process.communicate()
    if process.returncode != 0:
        logger.error("[autoHack] Standard code compilation failed.")
        raise RuntimeError("Standard code compilation failed.")
    logger.info("[autoHack] Standard code compiled successfully.")

    print("Compiling checker code.")
    logger.info("[autoHack] Compiling checker code.")
    logger.debug(
        f"[autoHack] Compile command: {config.getConfigEntry('commands.checker.compile')}"
    )
    process = subprocess.Popen(config.getConfigEntry("commands.checker.compile"))
    process.communicate()
    if process.returncode != 0:
        logger.error("[autoHack] Checker code compilation failed.")
        raise RuntimeError("Checker code compilation failed.")
    logger.info("[autoHack] Checker code compiled successfully.")

    print("Compiling generator code.")
    logger.info("[autoHack] Compiling generator code.")
    logger.debug(
        f"[autoHack] Compile command: {config.getConfigEntry('commands.generator.compile')}"
    )
    process = subprocess.Popen(config.getConfigEntry("commands.generator.compile"))
    process.communicate()
    if process.returncode != 0:
        logger.error("[autoHack] Generator code compilation failed.")
        raise RuntimeError("Generator code compilation failed.")


if __name__ == "__main__":
    try:
        compileCode()
    except RuntimeError as e:
        print(f"Error while compiling code.")
        logger.critical(f"[autoHack] Error: {e}")
        exit(1)
