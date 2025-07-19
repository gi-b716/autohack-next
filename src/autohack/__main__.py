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
    fileList = [
        ["commands.compile.source", "source code"],
        ["commands.compile.std", "standard code"],
        ["commands.compile.checker", "checker code"],
        ["commands.compile.generator", "generator code"],
    ]
    for file in fileList:
        compileCommand = config.getConfigEntry(file[0])
        print(f"Compiling {file[1]}.")
        logger.info(f"[autoHack] Compiling {file[1]}.")
        logger.debug(f"[autoHack] Compile command: {compileCommand}")
        process = subprocess.Popen(compileCommand)
        process.communicate()
        if process.returncode != 0:
            logger.error(f"[autoHack] {file[1].capitalize()} compilation failed.")
            raise RuntimeError(f"{file[1].capitalize()} compilation failed.")
        logger.info(f"[autoHack] {file[1].capitalize()} compiled successfully.")


if __name__ == "__main__":
    try:
        compileCode()
    except RuntimeError as e:
        print(f"Error while compiling code.")
        logger.critical(f"[autoHack] Error: {e}")
        exit(1)
