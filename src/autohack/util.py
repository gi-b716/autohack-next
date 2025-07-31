from .constant import *
import os


def checkDirectoryExists(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


def getTempInputFilePath(clientID: str) -> str:
    return os.path.join(TEMP_FOLDER_PATH, clientID, "input")


def getTempAnswerFilePath(clientID: str) -> str:
    return os.path.join(TEMP_FOLDER_PATH, clientID, "answer")
