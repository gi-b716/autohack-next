from .constant import *
from . import exception, function, checker, config, logger, util
import logging, shutil, time, uuid, os

if __name__ == "__main__":
    util.checkDirectoryExists(DATA_FOLDER_PATH)
    util.checkDirectoryExists(LOG_FOLDER_PATH)
    util.checkDirectoryExists(TEMP_FOLDER_PATH)
    if util.mswindows():
        os.system("attrib +h {0}".format(DATA_FOLDER_PATH))

    loggerObject = logger.Logger(LOG_FOLDER_PATH, logging.WARNING)
    logger = loggerObject.getLogger()
    config = config.Config(CONFIG_FILE_PATH, logger)
    logger.info(f'[autohack] Data folder path: "{DATA_FOLDER_PATH}"')
    clientID = str(uuid.uuid4())
    logger.info(f"[autohack] Client ID: {clientID}")
    logger.info("[autohack] Initialized.")

    symlinkFallback = False

    print(
        f"Hack data storaged to {CURRENT_HACK_DATA_FOLDER_PATH}.\n{' '*19}or {util.getHackDataStorageFolderPath(clientID)}\nLog file: {loggerObject.getLogFilePath()}"
    )
    util.checkDirectoryExists(util.getHackDataStorageFolderPath(clientID))
    if os.path.islink(CURRENT_HACK_DATA_FOLDER_PATH):
        os.unlink(CURRENT_HACK_DATA_FOLDER_PATH)
    elif os.path.isdir(CURRENT_HACK_DATA_FOLDER_PATH):
        shutil.rmtree(CURRENT_HACK_DATA_FOLDER_PATH)
    try:
        os.symlink(
            util.getHackDataStorageFolderPath(clientID),
            CURRENT_HACK_DATA_FOLDER_PATH,
            target_is_directory=True,
        )
    except OSError:
        symlinkFallback = True
        logger.warning("[autohack] Symlink creation failed. Using fallback method.")
        util.checkDirectoryExists(CURRENT_HACK_DATA_FOLDER_PATH)

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
            function.compileCode(file[0], file[1])
        except exception.CompilationError as e:
            logger.error(
                f"[autohack] {e.fileName.capitalize()} compilation failed: {e}"
            )
            print(f"\r{e}")
            exit(1)
        else:
            logger.info(f"[autohack] {file[1].capitalize()} compiled successfully.")
    print("\x1b[1K\rCompile finished.")

    dataCount, errorDataCount = 0, 0
    generateCommand = config.getConfigEntry("commands.run.generator")
    stdCommand = config.getConfigEntry("commands.run.std")
    sourceCommand = config.getConfigEntry("commands.run.source")
    timeLimit = config.getConfigEntry("time_limit")
    memoryLimit = config.getConfigEntry("memory_limit") * 1024 * 1024

    def saveErrorData(
        dataInput: bytes,
        dataAnswer: bytes,
        dataOutput: bytes,
        message: str,
        logMessage: str,
    ) -> None:
        global errorDataCount, logger
        errorDataCount += 1
        util.checkDirectoryExists(util.getHackDataFolderPath(errorDataCount))
        open(util.getInputFilePath(errorDataCount), "wb").write(dataInput)
        open(util.getAnswerFilePath(errorDataCount), "wb").write(dataAnswer)
        open(util.getOutputFilePath(errorDataCount), "wb").write(dataOutput)
        logger.warning(logMessage)
        print(message)

    startTime = time.time()

    while dataCount < config.getConfigEntry(
        "maximum_number_of_data"
    ) and errorDataCount < config.getConfigEntry("error_data_number_limit"):
        dataCount += 1

        try:
            logger.info(f"[autohack] Generating data {dataCount}.")
            print(f"\x1b[1K\r{dataCount}: Generate input.", end="")
            dataInput = function.generateInput(generateCommand, clientID)
        except exception.InputGenerationError as e:
            logger.error(f"[autohack] Input generation failed: {e}")
            print(f"\x1b[1K\r{e}")
            exit(1)

        try:
            logger.info(f"[autohack] Generating answer for data {dataCount}.")
            print(f"\x1b[1K\r{dataCount}: Generate answer.", end="")
            dataAnswer = function.generateAnswer(
                stdCommand,
                dataInput,
                clientID,
            )
        except exception.AnswerGenerationError as e:
            logger.error(f"[autohack] Answer generation failed: {e}")
            print(f"\x1b[1K\r{e}")
            exit(1)

        logger.info(f"[autohack] Run source code for data {dataCount}.")
        print(f"\x1b[1K\r{dataCount}: Run source code.", end="")
        result = function.runSourceCode(
            sourceCommand, dataInput, timeLimit, memoryLimit
        )

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

        checkerResult = checker.basicChecker(result.stdout, dataAnswer)
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
    if symlinkFallback:
        print(f"Saving hack data to data storage folder...", end="")
        logger.info(
            f"[autohack] Saving hack data to data storage folder: {util.getHackDataStorageFolderPath(clientID)}"
        )
        shutil.copytree(
            CURRENT_HACK_DATA_FOLDER_PATH,
            util.getHackDataStorageFolderPath(clientID),
            dirs_exist_ok=True,
        )
        print("\x1b[1K\rHack data saved to data storage folder.")
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
