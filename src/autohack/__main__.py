from autohack.core.constant import *
from autohack.core.exception import *
from autohack.core.path import *
from autohack.core.util import *
from autohack.lib.config import *
from autohack.lib.logger import *
from autohack.checker import *
import subprocess, traceback, argparse, logging, pathlib, time, uuid, os


def compileCode(compileCommand: str, fileName: str) -> None:
    try:
        process = subprocess.Popen(
            compileCommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
    except OSError:
        return
    output = process.communicate()[0]
    if process.returncode != 0:
        raise CompilationError(fileName, output, process.returncode)


def generateInput(generateCommand: str, clientID: str) -> bytes:
    try:
        process = subprocess.Popen(
            generateCommand, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
    except OSError:
        return b""
    dataInput = process.communicate()[0]
    if process.returncode != 0:
        raise InputGenerationError(clientID, process.returncode)
    return dataInput


def generateAnswer(generateCommand: str, dataInput: bytes, clientID: str) -> bytes:
    try:
        process = subprocess.Popen(
            generateCommand,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return b""
    dataAnswer = process.communicate(dataInput)[0]
    if process.returncode != 0:
        raise AnswerGenerationError(clientID, process.returncode)
    return dataAnswer


def runSourceCode(
    runCommand: str, dataInput: bytes, timeLimit: float | None, memoryLimit: int | None
) -> CodeRunner.Result:
    try:
        result = CodeRunner().run(
            runCommand,
            inputContent=dataInput,
            timeLimit=timeLimit,
            memoryLimit=memoryLimit,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return CodeRunner.Result(False, False, 0, b"", b"")
    return result


def main() -> None:
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

    args = argsParser.parse_args()

    if args.version:
        write(f"{VERSION}")
        exitProgram(0)

    if args.version_id:
        write(f"{VERSION_ID}")
        exitProgram(0)

    hideCursor()

    if args.debug:
        write("Debug mode enabled. Logging level set to DEBUG.", 2)

    ensureDirExists(LOG_FOLDER_PATH)

    loggerObj = Logger(LOG_FOLDER_PATH, logging.DEBUG if args.debug else logging.INFO)
    logger = loggerObj.getLogger()

    config = Config(CONFIG_FILE_PATH, DEFAULT_CONFIG, logger)

    clientID = str(uuid.uuid4())

    logger.info(f'[autohack] Data folder path: "{DATA_FOLDER_PATH}"')
    logger.info(f"[autohack] Client ID: {clientID}")
    logger.info(f"[autohack] Initialized. Version: {VERSION}")
    write(f"autohack-next {VERSION} - Client ID: {clientID}", 2)
    write(f"Hack data storaged to {getHackDataStorageFolderPath(clientID)}", 1)
    write(f"Log file: {loggerObj.getLogFilePath()}", 2)

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
            write(f"{e}", clear=True)
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
            dataInput = generateInput(generateCommand, clientID)
        except InputGenerationError as e:
            logger.error(
                f"[autohack] Input generation failed with return code {e.returnCode}."
            )
            # TODO: Show input file path
            write(f"{e}", clear=True)
            exitProgram(1)

        try:
            write(f"{dataCount}: Generate answer.", clear=True)
            logger.debug(f"[autohack] Generating answer for data {dataCount}.")
            dataAnswer = generateAnswer(
                stdCommand,
                dataInput,
                clientID,
            )
        except AnswerGenerationError as e:
            logger.error(
                f"[autohack] Answer generation failed with return code {e.returnCode}."
            )
            # TODO: Show input and answer file path
            write(f"{e}", clear=True)
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

        saveData, termMessage, logMessage, extMessage = False, "", "", None

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

        checkerResult = basicChecker(result.stdout, dataAnswer)
        if not checkerResult[0]:
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
                getHackDataFilePath(clientID, errorDataCount, inputFilePath), dataInput
            )
            writeData(
                getHackDataFilePath(clientID, errorDataCount, answerFilePath),
                dataAnswer,
            )
            writeData(
                getHackDataFilePath(clientID, errorDataCount, outputFilePath),
                result.stdout,
            )
            write(f"[{errorDataCount}]: {termMessage}", 1, True)
            if extMessage is not None:
                write(f"{(len(f'[{errorDataCount}]: ')-3)*' '} - {extMessage}", 1, True)
            logger.info(f"[autohack] {logMessage}")

    endTime = time.time()

    write(
        f"Finished. {dataCount} data generated, {errorDataCount} error data found.",
        1,
        True,
    )
    write(
        f"Time taken: {endTime - startTime:.2f} seconds, average {dataCount/(endTime - startTime):.2f} data per second, {(endTime - startTime)/dataCount:.2f} second per data.",
        1,
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
            1,
        )


if __name__ == "__main__" or os.getenv("AUTOHACK_ENTRYPOINT", "0") == "1":
    try:
        main()

    except KeyboardInterrupt:
        write(highlightText("Process interrupted by user."))

    except Exception as e:
        write(highlightText(f"Unhandled exception."), 1)

        errorFilePath = (
            pathlib.Path(os.getcwd()) / f"autohack-error.{time.time():.0f}.log"
        )
        errorFile = open(errorFilePath, "w+", encoding="utf-8")
        traceback.print_exc(file=errorFile)
        errorFile.close()

        write(highlightText(f"Error details saved to {errorFilePath}."), 2)
        # logger.critical(f"[autohack] Unhandled exception.")

        traceback.print_exc()

    exitProgram(0)
