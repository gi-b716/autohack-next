import os
import pathlib


def ensureDirExists(dirPath: pathlib.Path) -> None:
    dirPath.mkdir(parents=True, exist_ok=True)


def writeData(filePath: pathlib.Path, data: bytes) -> None:
    ensureDirExists(filePath.parent)
    open(filePath, "wb").write(data)


def readData(filePath: pathlib.Path) -> bytes:
    return open(filePath, "rb").read()


def getFolderSize(folderPath: pathlib.Path) -> int:
    # return shutil.disk_usage(folderPath).used
    totalSize = 0
    with os.scandir(folderPath) as entries:
        for entry in entries:
            if entry.is_file():
                totalSize += entry.stat().st_size
            elif entry.is_dir():
                totalSize += getFolderSize(pathlib.Path(entry.path))
    return totalSize
