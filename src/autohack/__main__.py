from .core.exception import *
from .core.path import *
from .core.util import *
from .lib.config import *
from .lib.logger import *
from .checker import *
from .function import *
import logging, shutil, time, uuid, sys, os

if __name__ == "__main__" or os.getenv("AUTOHACK_ENTRYPOINT", "0") == "1":
    if "--debug" in sys.argv:
        print("Debug mode enabled. Logging level set to DEBUG.")

    checkDirectoryExists(DATA_FOLDER_PATH)
    checkDirectoryExists(LOG_FOLDER_PATH)
    checkDirectoryExists(TEMP_FOLDER_PATH)
    if mswindows():
        os.system("attrib +h {0}".format(DATA_FOLDER_PATH))

    loggerObject = Logger(
        LOG_FOLDER_PATH,
        logging.DEBUG if "--debug" in sys.argv else logging.INFO,
    )
    logger = loggerObject.getLogger()
    config = Config(CONFIG_FILE_PATH, logger)
    logger.info(f'[autohack] Data folder path: "{DATA_FOLDER_PATH}"')
    clientID = str(uuid.uuid4())
    logger.info(f"[autohack] Client ID: {clientID}")
    logger.info("[autohack] Initialized.")

    symlinkFallback = False

    print(
        f"Hack data storaged to {CURRENT_HACK_DATA_FOLDER_PATH}.\n{' '*19}or {getHackDataStorageFolderPath(clientID)}\nLog file: {loggerObject.getLogFilePath()}"
    )
    checkDirectoryExists(getHackDataStorageFolderPath(clientID))
    if os.path.islink(CURRENT_HACK_DATA_FOLDER_PATH):
        os.unlink(CURRENT_HACK_DATA_FOLDER_PATH)
    elif os.path.isdir(CURRENT_HACK_DATA_FOLDER_PATH):
        shutil.rmtree(CURRENT_HACK_DATA_FOLDER_PATH)
    try:
        os.symlink(
            getHackDataStorageFolderPath(clientID),
            CURRENT_HACK_DATA_FOLDER_PATH,
            target_is_directory=True,
        )
    except OSError:
        symlinkFallback = True
        logger.warning("[autohack] Symlink creation failed. Using fallback method.")
        checkDirectoryExists(CURRENT_HACK_DATA_FOLDER_PATH)

    for i in range(3):
        print(f"\x1b[1K\rStarting in {3-i} seconds...", end="")
        time.sleep(1)

    fileList = [
        [config.getConfigEntry("commands.compile.source"), "source code"],
        [config.getConfigEntry("commands.compile.std"), "standard code"],
        [config.getConfigEntry("commands.compile.generator"), "generator code"],
    ]
    for file in fileList:
        print(f"\x1b[1K\rCompile {file[1]}.", end="")
        try:
            compileCode(file[0], file[1])
        except CompilationError as e:
            logger.error(
                f"[autohack] {e.fileName.capitalize()} compilation failed: {e}"
            )
            print(f"\r{e}")
            exit(1)
        else:
            logger.debug(f"[autohack] {file[1].capitalize()} compiled successfully.")
    print("\x1b[1K\rCompile finished.")

    dataCount, errorDataCount = 0, 0
    generateCommand = config.getConfigEntry("commands.run.generator")
    stdCommand = config.getConfigEntry("commands.run.std")
    sourceCommand = config.getConfigEntry("commands.run.source")
    timeLimit = config.getConfigEntry("time_limit")
    memoryLimit = config.getConfigEntry("memory_limit") * 1024 * 1024
    inputFilePath = config.getConfigEntry("paths.input")
    answerFilePath = config.getConfigEntry("paths.answer")
    outputFilePath = config.getConfigEntry("paths.output")

    def saveErrorData(
        dataInput: bytes,
        dataAnswer: bytes,
        dataOutput: bytes,
        message: str,
        logMessage: str,
    ) -> None:
        global errorDataCount, logger
        errorDataCount += 1
        checkDirectoryExists(getHackDataFolderPath(errorDataCount, inputFilePath))
        checkDirectoryExists(getHackDataFolderPath(errorDataCount, answerFilePath))
        checkDirectoryExists(getHackDataFolderPath(errorDataCount, outputFilePath))
        open(getHackDataFilePath(errorDataCount, inputFilePath), "wb").write(dataInput)
        open(getHackDataFilePath(errorDataCount, answerFilePath), "wb").write(
            dataAnswer
        )
        open(getHackDataFilePath(errorDataCount, outputFilePath), "wb").write(
            dataOutput
        )
        logger.info(logMessage)
        print(message)

    startTime = time.time()

    while dataCount < config.getConfigEntry(
        "maximum_number_of_data"
    ) and errorDataCount < config.getConfigEntry("error_data_number_limit"):
        dataCount += 1

        try:
            logger.debug(f"[autohack] Generating data {dataCount}.")
            print(f"\x1b[1K\r{dataCount}: Generate input.", end="")
            dataInput = generateInput(generateCommand, clientID)
        except InputGenerationError as e:
            logger.error(f"[autohack] Input generation failed: {e}")
            print(f"\x1b[1K\r{e}")
            exit(1)

        try:
            logger.debug(f"[autohack] Generating answer for data {dataCount}.")
            print(f"\x1b[1K\r{dataCount}: Generate answer.", end="")
            dataAnswer = generateAnswer(
                stdCommand,
                dataInput,
                clientID,
            )
        except AnswerGenerationError as e:
            logger.error(f"[autohack] Answer generation failed: {e}")
            print(f"\x1b[1K\r{e}")
            exit(1)

        logger.debug(f"[autohack] Run source code for data {dataCount}.")
        print(f"\x1b[1K\r{dataCount}: Run source code.", end="")
        result = runSourceCode(sourceCommand, dataInput, timeLimit, memoryLimit)

        if result.memoryOut:
            saveErrorData(
                dataInput,
                dataAnswer,
                result.stdout,
                f"\x1b[1K\r[{errorDataCount+1}]: Memory limit exceeded for data {dataCount}.",
                f"[autohack] Memory limit exceeded for data {dataCount}.",
            )
            continue
        elif result.timeOut:
            saveErrorData(
                dataInput,
                dataAnswer,
                result.stdout,
                f"\x1b[1K\r[{errorDataCount+1}]: Time limit exceeded for data {dataCount}.",
                f"[autohack] Time limit exceeded for data {dataCount}.",
            )
            continue
        elif result.returnCode != 0:
            saveErrorData(
                dataInput,
                dataAnswer,
                result.stdout,
                f"\x1b[1K\r[{errorDataCount+1}]: Runtime error for data {dataCount} with return code {result.returnCode}.",
                f"[autohack] Runtime error for data {dataCount} with return code {result.returnCode}.",
            )
            continue

        checkerResult = basicChecker(result.stdout, dataAnswer)
        if not checkerResult[0]:
            saveErrorData(
                dataInput,
                dataAnswer,
                result.stdout,
                f"\x1b[1K\r[{errorDataCount+1}]: Wrong answer for data {dataCount}.\n{(len(f"[{errorDataCount+1}]: ")-3)*' '} - {checkerResult[1]}",
                f"[autohack] Wrong answer for data {dataCount}. Checker output: {checkerResult[1]}",
            )

    endTime = time.time()

    print(
        f"\x1b[1K\rFinished. {dataCount} data generated, {errorDataCount} error data found.\nTime taken: {endTime - startTime:.2f} seconds, average {dataCount/(endTime - startTime):.2f} data per second, {(endTime - startTime)/dataCount:.2f} second per data."
    )
    if errorDataCount > 0:
        if symlinkFallback:
            print(f"Saving hack data to data storage folder...", end="")
            shutil.copytree(
                CURRENT_HACK_DATA_FOLDER_PATH,
                getHackDataStorageFolderPath(clientID),
                dirs_exist_ok=True,
            )
            print("\x1b[1K\rHack data saved to data storage folder.")
            logger.info(
                f"[autohack] Hack data saved to data storage folder: {getHackDataStorageFolderPath(clientID)}"
            )
    else:
        shutil.rmtree(getHackDataStorageFolderPath(clientID))
        print("No error data found. Hack data folder removed.")
        logger.info("[autohack] No error data found. Hack data folder removed.")
    if (
        os.path.exists(HACK_DATA_STORAGE_FOLDER_PATH)
        and os.path.getsize(HACK_DATA_STORAGE_FOLDER_PATH) > 256 * 1024 * 1024
    ):
        logger.warning(
            f"[autohack] Hack data storage folder size exceeds 256 MB: {HACK_DATA_STORAGE_FOLDER_PATH}"
        )
        print(
            f"Warning: Hack data storage folder size exceeds 256 MB: {HACK_DATA_STORAGE_FOLDER_PATH}"
        )

    comment = input("Comment (optional): ")
    open(RECORD_FILE_PATH, "a+").write(
        f"{time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))} / {clientID}\n{dataCount} data generated, {errorDataCount} error data found.\nTime taken: {endTime - startTime:.2f} seconds, average {dataCount/(endTime - startTime):.2f} data per second, {(endTime - startTime)/dataCount:.2f} second per data.\n{comment}\n\n"
    )
    print(f"Record saved to {RECORD_FILE_PATH}.")
    logger.info(f"[autohack] Record saved to {RECORD_FILE_PATH}.")
