from .constant import *
from . import exception, function, checker, config, logger, util
import logging, shutil, uuid, os

if __name__ == "__main__":
    util.checkDirectoryExists(DATA_FOLDER_PATH)
    util.checkDirectoryExists(LOG_FOLDER_PATH)
    util.checkDirectoryExists(TEMP_FOLDER_PATH)
    if util.mswindows():
        os.system("attrib +h {0}".format(DATA_FOLDER_PATH))

    # TODO Remember to delete DEBUG tag
    logger = logger.Logger(LOG_FOLDER_PATH, logging.WARNING).getLogger()
    config = config.Config(CONFIG_FILE_PATH, logger)
    logger.info(f'[autohack] Data folder path: "{DATA_FOLDER_PATH}"')
    clientID = str(uuid.uuid4())
    logger.info(f"[autohack] Client ID: {clientID}")
    logger.info("[autohack] Initialized.")

    if os.path.exists(HACK_DATA_FOLDER_PATH):
        shutil.rmtree(HACK_DATA_FOLDER_PATH)

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
        open(
            os.path.join(util.getHackDataFolderPath(errorDataCount), "input"), "wb"
        ).write(dataInput)
        open(
            os.path.join(util.getHackDataFolderPath(errorDataCount), "answer"), "wb"
        ).write(dataAnswer)
        open(
            os.path.join(util.getHackDataFolderPath(errorDataCount), "output"), "wb"
        ).write(dataOutput)
        logger.warning(logMessage)
        print(message)

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
                f"\x1b[1K\rMemory limit exceeded for data {dataCount}. Hack data saved to {util.getHackDataFolderPath(errorDataCount)}.",
                f"[autohack] Memory limit exceeded for data {dataCount}.",
            )
            continue
        elif result.timeOut:
            saveErrorData(
                dataInput,
                dataAnswer,
                result.stdout,
                f"\x1b[1K\rTime limit exceeded for data {dataCount}. Hack data saved to {util.getHackDataFolderPath(errorDataCount)}.",
                f"[autohack] Time limit exceeded for data {dataCount}.",
            )
            continue
        elif result.returnCode != 0:
            saveErrorData(
                dataInput,
                dataAnswer,
                result.stdout,
                f"\x1b[1K\rRuntime error for data {dataCount} with return code {result.returnCode}. Hack data saved to {util.getHackDataFolderPath(errorDataCount)}.",
                f"[autohack] Runtime error for data {dataCount} with return code {result.returnCode}.",
            )
            continue

        checkerResult = checker.basicChecker(result.stdout, dataAnswer)
        if not checkerResult[0]:
            saveErrorData(
                dataInput,
                dataAnswer,
                result.stdout,
                f"\x1b[1K\rWrong answer for data {dataCount}. Hack data saved to {util.getHackDataFolderPath(errorDataCount)}. Checker output: {checkerResult[1]}",
                f"[autohack] Wrong answer for data {dataCount}. Checker output: {checkerResult[1]}",
            )

    print(
        f"\x1b[1K\rFinished. {dataCount} data generated, {errorDataCount} error data found."
    )
