from autohack.core.checker import *
from autohack.core.constant import *
from autohack.core.exception import *
from autohack.core.path import *
from autohack.core.util import *
from autohack.core.run import *
from autohack.lib.config import *
from autohack.lib.logger import *
from typing import Callable
import traceback, argparse, colorama, logging, time, uuid, os

CLIENT_ID = str(uuid.uuid4())
LOG_TIME = time.localtime()


def main() -> None:
    global CLIENT_ID, LOG_TIME

    argsParser = argparse.ArgumentParser(
        prog="autohack", description="autohack-next - Automated hack data generator"
    )
    argsParser.add_argument(
        "--version", action="store_true", help="Show version information"
    )
    argsParser.add_argument("--version-id", action="store_true", help="Show version ID")
    argsParser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with DEBUG logging level",
    )
    # TODO: 添加一个参数用于清除过往数据

    args = argsParser.parse_args()

    if args.version:
        write(f"{VERSION}")
        exitProgram(0, True)

    if args.version_id:
        write(f"{VERSION_ID}")
        exitProgram(0, True)

    hideCursor()

    if args.debug:
        write("Debug mode enabled. Logging level set to DEBUG.", 2)

    ensureDirExists(CHECKER_FOLDER_PATH)
    ensureDirExists(LOG_FOLDER_PATH)

    loggerObj = Logger(
        LOG_FOLDER_PATH, logging.DEBUG if args.debug else logging.INFO, LOG_TIME
    )
    logger = loggerObj.getLogger()

    config = Config(CONFIG_FILE_PATH, DEFAULT_CONFIG, logger)

    logger.info(f'[autohack] Data folder path: "{DATA_FOLDER_PATH}"')
    logger.info(f"[autohack] Client ID: {CLIENT_ID}")
    logger.info(f"[autohack] Initialized. Version: {VERSION}")
    write(f"autohack-next {VERSION} - Client ID: {CLIENT_ID}", 2)
    write(
        f"Hack data storaged to {getHackDataStorageFolderPath(CLIENT_ID, LOG_TIME)}", 1
    )
    write(f"Log file: {loggerObj.getLogFilePath()}", 1)
    write(f"Error export to {getExportFolderPath(LOG_TIME, CLIENT_ID)}", 1)
    write(f"Custom checker folder: {CHECKER_FOLDER_PATH}", 2)

    write("Activating checker...")

    currentChecker: checkerType = lambda l, o, a, ar: (False, "No checker activated.")
    deactivateFunc: deactivateType = emptyDeactivate

    try:
        getCheckerResult = getChecker(
            CHECKER_FOLDER_PATH,
            config.getConfigEntry("checker.name"),
            config.getConfigEntry("checker.args"),
        )
        currentChecker = getCheckerResult[0]
        deactivateFunc = getCheckerResult[1]
    except Exception as e:
        logger.critical(f"[autohack] {e}")
        write("Checker activation failed.", 1, True)
        write(highlightText(e.__str__()))
        exitProgram(1)

    write("Checker activated.", 1, True)

    for i in range(WAIT_TIME_BEFORE_START):
        write(f"Starting in {WAIT_TIME_BEFORE_START-i} seconds...", clear=True)
        time.sleep(1)

    fileList = [
        [config.getConfigEntry("commands.compile.source"), "source code"],
        [config.getConfigEntry("commands.compile.std"), "standard code"],
        [config.getConfigEntry("commands.compile.generator"), "generator code"],
    ]
    for file in fileList:
        write(f"Compile {file[1]}.", clear=True)
        try:
            compileCode(file[0], file[1])
        except CompilationError as e:
            logger.error(
                f"[autohack] {file[1].capitalize()} compilation failed with return code {e.returnCode} and message:\n{e.message.decode()}"
            )
            write(highlightText(e.__str__()), 2, True)
            write(e.getMessage())
            exitProgram(1)
        else:
            logger.debug(f"[autohack] {file[1].capitalize()} compiled successfully.")

    write("Compile finished.", 2, True)

    dataCount, errorDataCount = 0, 0
    lastStatusError = False
    generateCommand = config.getConfigEntry("commands.run.generator")
    stdCommand = config.getConfigEntry("commands.run.std")
    sourceCommand = config.getConfigEntry("commands.run.source")
    timeLimit = config.getConfigEntry("time_limit") / 1000
    memoryLimit = config.getConfigEntry("memory_limit") * 1024 * 1024
    inputFilePath = config.getConfigEntry("paths.input")
    answerFilePath = config.getConfigEntry("paths.answer")
    outputFilePath = config.getConfigEntry("paths.output")
    maximumDataLimit = config.getConfigEntry("maximum_number_of_data")
    errorDataLimit = config.getConfigEntry("error_data_number_limit")
    refreshSpeed = config.getConfigEntry("refresh_speed")
    checkerArgs = config.getConfigEntry("checker.args")

    outputEndl()
    write(
        "Time taken: 0.00 seconds, average 0.00 data per second, 0.00 second per data."
    )
    prevLine()

    startTime = time.time()

    while (maximumDataLimit <= 0 or dataCount < maximumDataLimit) and (
        errorDataLimit <= 0 or errorDataCount < errorDataLimit
    ):
        dataInput = b""
        dataAnswer = b""

        dataCount += 1

        try:
            write(f"{dataCount}: Generate input.", clear=True)
            logger.debug(f"[autohack] Generating data {dataCount}.")
            dataInput = generateInput(generateCommand, CLIENT_ID)
        except InputGenerationError as e:
            logger.error(
                f"[autohack] Input generation failed with return code {e.returnCode}."
            )
            write(highlightText(e.__str__()), 1, True)
            inputExportPath = getExportDataPath(
                getExportFolderPath(LOG_TIME, CLIENT_ID), "input"
            )
            writeData(inputExportPath, dataInput)
            write(highlightText(f"Input data saved to {inputExportPath}"), clear=True)
            exitProgram(1)

        try:
            write(f"{dataCount}: Generate answer.", clear=True)
            logger.debug(f"[autohack] Generating answer for data {dataCount}.")
            dataAnswer = generateAnswer(
                stdCommand,
                dataInput,
                CLIENT_ID,
            )
        except AnswerGenerationError as e:
            logger.error(
                f"[autohack] Answer generation failed with return code {e.returnCode}."
            )
            write(highlightText(e.__str__()), 1, True)
            inputExportPath = getExportDataPath(
                getExportFolderPath(LOG_TIME, CLIENT_ID), "input"
            )
            writeData(inputExportPath, dataInput)
            write(highlightText(f"Input data saved to {inputExportPath}"), 1, True)
            answerExportPath = getExportDataPath(
                getExportFolderPath(LOG_TIME, CLIENT_ID), "answer"
            )
            writeData(answerExportPath, dataAnswer)
            write(highlightText(f"Answer data saved to {answerExportPath}"), clear=True)
            exitProgram(1)

        write(f"{dataCount}: Run source code.", clear=True)
        logger.debug(f"[autohack] Run source code for data {dataCount}.")
        result = runSourceCode(sourceCommand, dataInput, timeLimit, memoryLimit)
        if result.stdout is None:
            result.stdout = b""
        if result.stderr is None:
            result.stderr = b""

        # TODO: Refresh when running exe. Use threading or async?
        if dataCount % refreshSpeed == 0 or lastStatusError:
            lastStatusError = False
            currentTime = time.time()
            outputEndl()
            write(
                f"Time taken: {currentTime - startTime:.2f} seconds, average {dataCount/(currentTime - startTime):.2f} data per second, {(currentTime - startTime)/dataCount:.2f} second per data.{f" ({dataCount*100/maximumDataLimit:.0f}%)" if maximumDataLimit > 0 else ""}",
                clear=True,
            )
            prevLine()

        saveData, termMessage, logMessage, extMessage, exitAfterSave = (
            False,
            "",
            "",
            None,
            False,
        )

        if result.memoryOut:
            saveData = True
            termMessage = logMessage = f"Memory limit exceeded for data {dataCount}."
        elif result.timeOut:
            saveData = True
            termMessage = logMessage = f"Time limit exceeded for data {dataCount}."
        elif result.returnCode != 0:
            saveData = True
            termMessage = logMessage = (
                f"Runtime error for data {dataCount} with return code {result.returnCode}."
            )

        checkerResult = (False, "Checker not executed.")
        try:
            checkerResult = currentChecker(
                dataInput, result.stdout, dataAnswer, checkerArgs
            )
        except Exception as e:
            saveData = True
            termMessage = f"Checker error for data {dataCount}."
            logMessage = f"Checker error for data {dataCount}. Exception: {e}"
            extMessage = f"Traceback:\n{traceback.format_exc()}"
            checkerResult = (False, "Checker exception occurred.")
            exitAfterSave = True

        if not saveData and not checkerResult[0]:
            saveData = True
            termMessage = f"Wrong answer for data {dataCount}."
            logMessage = (
                f"Wrong answer for data {dataCount}. Checker output: {checkerResult[1]}"
            )
            extMessage = checkerResult[1]

        if saveData:
            lastStatusError = True
            errorDataCount += 1
            writeData(
                getHackDataFilePath(
                    getHackDataStorageFolderPath(CLIENT_ID, LOG_TIME),
                    errorDataCount,
                    inputFilePath,
                ),
                dataInput,
            )
            writeData(
                getHackDataFilePath(
                    getHackDataStorageFolderPath(CLIENT_ID, LOG_TIME),
                    errorDataCount,
                    answerFilePath,
                ),
                dataAnswer,
            )
            writeData(
                getHackDataFilePath(
                    getHackDataStorageFolderPath(CLIENT_ID, LOG_TIME),
                    errorDataCount,
                    outputFilePath,
                ),
                result.stdout,
            )
            write(f"[{errorDataCount}]: {termMessage}", 1, True)
            if extMessage is not None:
                write(f"{(len(f'[{errorDataCount}]: ')-3)*' '} - {extMessage}", 1, True)
            logger.info(f"[autohack] {logMessage}")

        if exitAfterSave:
            write("Exiting due to checker exception.", clear=True)
            exitProgram(0)

    endTime = time.time()

    write(
        f"Finished. {dataCount} data generated, {errorDataCount} error data found.",
        1,
        True,
    )
    write(
        f"Time taken: {endTime - startTime:.2f} seconds, average {dataCount/(endTime - startTime):.2f} data per second, {(endTime - startTime)/dataCount:.2f} second per data.",
        2,
        True,
    )

    # if errorDataCount == 0:
    #     shutil.rmtree(getHackDataStorageFolderPath(clientID))
    #     write("No error data found. Hack data folder removed.", 1)
    #     logger.info("[autohack] No error data found. Hack data folder removed.")

    if (
        HACK_DATA_STORAGE_FOLDER_PATH.exists()
        and HACK_DATA_STORAGE_FOLDER_PATH.stat().st_size > DATA_FOLDER_MAX_SIZE
    ):
        logger.warning(
            f"[autohack] Hack data storage folder size exceeds 256 MB: {HACK_DATA_STORAGE_FOLDER_PATH}"
        )
        write(
            f"Warning: Hack data storage folder size exceeds 256 MB: {HACK_DATA_STORAGE_FOLDER_PATH}",
            2,
        )

    write("Deactivating checker...")
    deactivateFunc(config.getConfigEntry("checker.args"))
    write("Checker deactivated.", 1, True)

    write("Executing post process command.", 1)
    os.system(config.getConfigEntry("command_at_end"))
    logger.info("[autohack] Finished.")


if __name__ == "__main__" or os.getenv("AUTOHACK_ENTRYPOINT", "0") == "1":
    colorama.just_fix_windows_console()

    try:
        main()

    except KeyboardInterrupt:
        write(highlightText("Process interrupted by user."))

    except Exception as e:
        write(highlightText(f"Unhandled exception."), 1)

        errorFilePath = getExportFolderPath(LOG_TIME, CLIENT_ID) / f"error.log"
        ensureDirExists(errorFilePath.parent)
        errorFile = open(errorFilePath, "w+", encoding="utf-8")
        traceback.print_exc(file=errorFile)
        errorFile.close()

        write(highlightText(f"Error details saved to {errorFilePath}"), 2)
        # logger.critical(f"[autohack] Unhandled exception.")

        traceback.print_exc()
        exitProgram(1)

    exitProgram(0)
