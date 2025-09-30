from autohack.core.checker import *
from autohack.core.constant import *
from autohack.core.exception import *
from autohack.core.path import *
from autohack.core.util import *
from autohack.core.run import *
from autohack.lib.config import *
from autohack.lib.logger import *
from autohack.lib.i18n import *
import traceback, argparse, colorama, logging, time, uuid, os

CLIENT_ID = str(uuid.uuid4())
LOG_TIME = time.localtime()


def main() -> None:
    global CLIENT_ID, LOG_TIME

    argsParser = argparse.ArgumentParser(prog="autohack", description="autohack-next - Automated hack data generator")
    argsParser.add_argument("--version", action="store_true", help="Show version information")
    argsParser.add_argument("--version-id", action="store_true", help="Show version ID")
    argsParser.add_argument("--debug", action="store_true", help="Enable debug mode with DEBUG logging level")
    argsParser.add_argument("--reset-global-config", action="store_true", help="Reset the global config file (global_config.json)")
    # TODO: 添加一个参数用于清除过往数据

    args = argsParser.parse_args()

    if args.version:
        write(f"{VERSION}")
        exitProgram(0, True)

    if args.version_id:
        write(f"{VERSION_ID}")
        exitProgram(0, True)

    hideCursor()

    if args.reset_global_config and GLOBAL_CONFIG_FILE_PATH.exists():
        os.remove(GLOBAL_CONFIG_FILE_PATH)

    # if args.debug:
    #     write("Debug mode enabled. Logging level set to DEBUG.", 2)

    ensureDirExists(CHECKER_FOLDER_PATH)
    ensureDirExists(LOG_FOLDER_PATH)

    loggerObj = Logger(LOG_FOLDER_PATH, logging.DEBUG if args.debug else logging.INFO, LOG_TIME)
    logger = loggerObj.getLogger()

    I18n = I18N(TRANSLATION_FOLDER_PATH, logger)
    _ = I18n.translate

    if not GLOBAL_CONFIG_FILE_PATH.exists():
        logger.info("[autohack] Global config file not found. Creating new one.")
        write("Welcome to autohack-next!", 1)
        write("A global config file will be created.", 1)
        write("Please select your preferred language:", 1)
        for i, (langID) in enumerate(LANGUAGE_MAPS):
            write(f"  {i+1}: {langID} / {I18N(TRANSLATION_FOLDER_PATH, logger).translate("language-info", langID)}", 1)
        showCursor()
        while True:
            result = inputMessage("Enter the number of your preferred language: ", 0, True)
            if result.isdigit() and 1 <= int(result) <= len(LANGUAGE_MAPS):
                selectedLang = LANGUAGE_MAPS[int(result) - 1]
                break
            write("Invalid input. Please enter a valid number.")
            prevLine()
        globalConfig = Config(GLOBAL_CONFIG_FILE_PATH, DEFAULT_GLOBAL_CONFIG, logger)
        globalConfig.modifyConfigEntry("language", selectedLang)
        I18n.setDefaultLanguage(selectedLang)
        writeMessage(I18n, "__main__.language-select.result", _("language-info"), endl=1)
        writeMessage(I18n, "__main__.language-select.info", GLOBAL_CONFIG_FILE_PATH, endl=2)

    globalConfig = Config(GLOBAL_CONFIG_FILE_PATH, DEFAULT_GLOBAL_CONFIG, logger)

    config = Config(CONFIG_FILE_PATH, DEFAULT_CONFIG, logger, True)

    logger.info(f'[autohack] Data folder path: "{DATA_FOLDER_PATH}"')
    logger.info(f"[autohack] Client ID: {CLIENT_ID}")
    logger.info(f"[autohack] Initialized. Version: {VERSION}")
    writeMessage(I18n, "__main__.start.version", VERSION, CLIENT_ID, endl=2)
    writeMessage(I18n, "__main__.start.data", getHackDataStorageFolderPath(CLIENT_ID, LOG_TIME), endl=1)
    writeMessage(I18n, "__main__.start.log", loggerObj.getLogFilePath(), endl=1)
    writeMessage(I18n, "__main__.start.export", getExportFolderPath(LOG_TIME, CLIENT_ID), endl=1)
    writeMessage(I18n, "__main__.start.checker", CHECKER_FOLDER_PATH, endl=2)

    for i in range(WAIT_TIME_BEFORE_START):
        writeMessage(I18n, "__main__.countdown", WAIT_TIME_BEFORE_START - i, clear=True)
        time.sleep(1)

    fileList = [
        [config.getConfigEntry("commands.compile.source"), "__main__.compile.filename.source"],
        [config.getConfigEntry("commands.compile.std"), "__main__.compile.filename.std"],
        [config.getConfigEntry("commands.compile.generator"), "__main__.compile.filename.generator"],
    ]
    for file in fileList:
        writeMessage(I18n, "__main__.compile.doing", _(file[1]), clear=True)
        try:
            compileCode(file[0], file[1])
        except autohackCompilationError as e:
            logger.error(
                f"[autohack] {_(file[1], LOGGER_LANGUAGE_ID).capitalize()} compilation failed with return code {e.returnCode} and message:\n{e.output.decode(errors="ignore")}"
            )
            writeMessage(I18n, "__main__.compile.error", _(file[1]).capitalize(), e.returnCode, endl=2, clear=True, highlight=True)
            write(e.output.decode(errors="ignore"))
            exitProgram(1)
        else:
            logger.debug(f"[autohack] {_(file[1], LOGGER_LANGUAGE_ID).capitalize()} compiled successfully.")
    writeMessage(I18n, "__main__.compile.finish", endl=1, clear=True)

    writeMessage(I18n, "__main__.activate-checker.doing", config.getConfigEntry("checker.name"))
    currentChecker: checkerType = lambda l, o, a, ar: (False, _("__main__.activate-checker.no-checker-message"))
    deactivateFunc: deactivateType = emptyDeactivate
    try:
        getCheckerResult = getChecker(CHECKER_FOLDER_PATH, config.getConfigEntry("checker.name"), config.getConfigEntry("checker.args"))
        currentChecker = getCheckerResult[0]
        deactivateFunc = getCheckerResult[1]
    except Exception as e:
        logger.critical(f"[autohack] {e}")
        writeMessage(I18n, "__main__.activate-checker.failed", endl=1, clear=True)
        write(str(e), highlight=True)
        exitProgram(1)
    writeMessage(I18n, "__main__.activate-checker.finish", config.getConfigEntry("checker.name"), endl=2, clear=True)

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

    def updateStatus(total: float, averagePerS: float, averagePerData: float, addtional: str) -> None:
        # write(
        #     f"Time taken: {total:.2f} seconds, average {averagePerS:.2f} data per second, {averagePerData:.2f} second per data.{addtional}",
        #     clear=True,
        # )
        writeMessage(I18n, "__main__.status", f"{total:.2f}", f"{averagePerS:.2f}", f"{averagePerData:.2f}", addtional, clear=True)

    outputEndl()
    updateStatus(0.0, 0.0, 0.0, " (0%)" if maximumDataLimit > 0 else "")
    prevLine()

    startTime = time.time()

    while (maximumDataLimit <= 0 or dataCount < maximumDataLimit) and (errorDataLimit <= 0 or errorDataCount < errorDataLimit):
        dataInput = b""
        dataAnswer = b""

        dataCount += 1

        try:
            # write(f"{dataCount}: Generate input.", clear=True)
            writeMessage(I18n, "__main__.main.generate-input", dataCount, clear=True)
            logger.debug(f"[autohack] Generating data {dataCount}.")
            dataInput = generateInput(generateCommand, CLIENT_ID)
        except InputGenerationError as e:
            logger.error(f"[autohack] Input generation failed with return code {e.returnCode}.")
            write(highlightText(e.__str__()), 1, True)
            inputExportPath = getExportDataPath(getExportFolderPath(LOG_TIME, CLIENT_ID), "input")
            writeData(inputExportPath, dataInput)
            write(highlightText(f"Input data saved to {inputExportPath}"), clear=True)
            exitProgram(1)

        try:
            # write(f"{dataCount}: Generate answer.", clear=True)
            writeMessage(I18n, "__main__.main.generate-answer", dataCount, clear=True)
            logger.debug(f"[autohack] Generating answer for data {dataCount}.")
            dataAnswer = generateAnswer(stdCommand, dataInput, CLIENT_ID)
        except AnswerGenerationError as e:
            logger.error(f"[autohack] Answer generation failed with return code {e.returnCode}.")
            write(highlightText(e.__str__()), 1, True)
            inputExportPath = getExportDataPath(getExportFolderPath(LOG_TIME, CLIENT_ID), "input")
            writeData(inputExportPath, dataInput)
            write(highlightText(f"Input data saved to {inputExportPath}"), 1, True)
            answerExportPath = getExportDataPath(getExportFolderPath(LOG_TIME, CLIENT_ID), "answer")
            writeData(answerExportPath, dataAnswer)
            write(highlightText(f"Answer data saved to {answerExportPath}"), clear=True)
            exitProgram(1)

        # write(f"{dataCount}: Run source code.", clear=True)
        writeMessage(I18n, "__main__.main.run-source", dataCount, clear=True)
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
            # write(
            #     f"Time taken: {currentTime - startTime:.2f} seconds, average {dataCount/(currentTime - startTime):.2f} data per second, {(currentTime - startTime)/dataCount:.2f} second per data.{f" ({dataCount*100/maximumDataLimit:.0f}%)" if maximumDataLimit > 0 else ""}",
            #     clear=True,
            # )
            updateStatus(
                currentTime - startTime,
                dataCount / (currentTime - startTime),
                (currentTime - startTime) / dataCount,
                f" ({dataCount*100/maximumDataLimit:.0f}%)" if maximumDataLimit > 0 else "",
            )
            prevLine()

        saveData, termMessage, logMessage, extMessage, exitAfterSave = (False, "", "", None, False)

        if result.memoryOut:
            saveData = True
            termMessage = logMessage = f"Memory limit exceeded for data {dataCount}."
        elif result.timeOut:
            saveData = True
            termMessage = logMessage = f"Time limit exceeded for data {dataCount}."
        elif result.returnCode != 0:
            saveData = True
            termMessage = logMessage = f"Runtime error for data {dataCount} with return code {result.returnCode}."

        checkerResult = (False, "Checker not executed.")
        try:
            checkerResult = currentChecker(dataInput, result.stdout, dataAnswer, checkerArgs)
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
            logMessage = f"Wrong answer for data {dataCount}. Checker output: {checkerResult[1]}"
            extMessage = checkerResult[1]

        if saveData:
            lastStatusError = True
            errorDataCount += 1
            writeData(getHackDataFilePath(getHackDataStorageFolderPath(CLIENT_ID, LOG_TIME), errorDataCount, inputFilePath), dataInput)
            writeData(getHackDataFilePath(getHackDataStorageFolderPath(CLIENT_ID, LOG_TIME), errorDataCount, answerFilePath), dataAnswer)
            writeData(getHackDataFilePath(getHackDataStorageFolderPath(CLIENT_ID, LOG_TIME), errorDataCount, outputFilePath), result.stdout)
            write(f"[{errorDataCount}]: {termMessage}", 1, True)
            if extMessage is not None:
                write(f"{(len(f'[{errorDataCount}]: ')-3)*' '} - {extMessage}", 1, True)
            logger.info(f"[autohack] {logMessage}")

        if exitAfterSave:
            write("Exiting due to checker exception.", clear=True)
            exitProgram(0)

    endTime = time.time()

    writeMessage(I18n, "__main__.main.finish", dataCount, errorDataCount, endl=1, clear=True)
    # write(
    #     f"Time taken: {endTime - startTime:.2f} seconds, average {dataCount/(endTime - startTime):.2f} data per second, {(endTime - startTime)/dataCount:.2f} second per data.",
    #     2,
    #     True,
    # )
    updateStatus(endTime - startTime, dataCount / (endTime - startTime), (endTime - startTime) / dataCount, "")
    outputEndl(2)

    # if errorDataCount == 0:
    #     shutil.rmtree(getHackDataStorageFolderPath(clientID))
    #     write("No error data found. Hack data folder removed.", 1)
    #     logger.info("[autohack] No error data found. Hack data folder removed.")

    if HACK_DATA_STORAGE_FOLDER_PATH.exists() and getFolderSize(HACK_DATA_STORAGE_FOLDER_PATH) > DATA_FOLDER_MAX_SIZE * 1024 * 1024:
        logger.warning(f"[autohack] Hack data storage folder size exceeds {DATA_FOLDER_MAX_SIZE} MB: {HACK_DATA_STORAGE_FOLDER_PATH}")
        # write(f"Warning: Hack data storage folder size exceeds {DATA_FOLDER_MAX_SIZE} MB: {HACK_DATA_STORAGE_FOLDER_PATH}", 2)
        writeMessage(I18n, "__main__.data-folder-size-warning", DATA_FOLDER_MAX_SIZE, HACK_DATA_STORAGE_FOLDER_PATH, endl=2, highlight=True)

    writeMessage(I18n, "__main__.deactivate-checker.doing")
    # TODO: error handling
    deactivateFunc(config.getConfigEntry("checker.args"))
    writeMessage(I18n, "__main__.deactivate-checker.finish", endl=1, clear=True)

    writeMessage(I18n, "__main__.post-command", endl=1)
    os.system(config.getConfigEntry("command_at_end"))
    logger.info("[autohack] Finished.")


if __name__ == "__main__" or os.getenv("AUTOHACK_ENTRYPOINT", "0") == "1":
    colorama.just_fix_windows_console()

    try:
        main()

    except KeyboardInterrupt:
        write("Process interrupted by user.", highlight=True)

    except Exception as e:
        write("Unhandled exception.", 1, highlight=True)

        errorFilePath = getExportFolderPath(LOG_TIME, CLIENT_ID) / f"error.log"
        ensureDirExists(errorFilePath.parent)
        errorFile = open(errorFilePath, "w+", encoding="utf-8")
        traceback.print_exc(file=errorFile)
        errorFile.close()

        write(f"Error details saved to {errorFilePath}", 2, highlight=True)
        # logger.critical(f"[autohack] Unhandled exception.")

        traceback.print_exc()
        exitProgram(1)

    exitProgram(0)
