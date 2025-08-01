from .constant import *
from . import exception, function, checker, config, logger, util
import logging, shutil, uuid, os, threading, queue, time
from concurrent.futures import ThreadPoolExecutor

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

    start = time.time()
    dataCount, errorDataCount = 0, 0
    generateCommand = config.getConfigEntry("commands.run.generator")
    stdCommand = config.getConfigEntry("commands.run.std")
    sourceCommand = config.getConfigEntry("commands.run.source")
    timeLimit = config.getConfigEntry("time_limit")
    memoryLimit = config.getConfigEntry("memory_limit") * 1024 * 1024
    threadCount = config.getConfigEntry("thread_count")

    # Thread-safe counters and locks
    dataCountLock = threading.Lock()
    errorCountLock = threading.Lock()
    threadStatus = {}  # Dictionary to store each thread's status
    statusLock = threading.Lock()

    def updateThreadStatus(threadId: int, status: str) -> None:
        """Update the status for a specific thread and refresh display"""
        with statusLock:
            threadStatus[threadId] = status
            # Save current cursor position
            print("\x1b[s", end="")  # Save cursor position

            # Move up to the thread's line and update it
            lines_to_move_up = threadCount - threadId + 1
            print(f"\x1b[{lines_to_move_up}A", end="")  # Move up
            print(f"\x1b[K", end="")  # Clear line
            print(f"Thread #{threadId}: {status}", end="")

            # Restore cursor position
            print("\x1b[u", end="", flush=True)  # Restore cursor position

    # Reserve space for thread status lines and initialize
    for i in range(1, threadCount + 1):
        print(f"Thread #{i}: Starting...")

    # Initialize thread status dictionary
    for i in range(1, threadCount + 1):
        threadStatus[i] = "Starting..."

    def saveErrorData(
        dataInput: bytes,
        dataAnswer: bytes,
        dataOutput: bytes,
        message: str,
        logMessage: str,
        threadId: int,
    ) -> None:
        global errorDataCount, logger
        with errorCountLock:
            errorDataCount += 1
            currentErrorCount = errorDataCount

        util.checkDirectoryExists(util.getHackDataFolderPath(currentErrorCount))
        open(
            os.path.join(util.getHackDataFolderPath(currentErrorCount), "input"), "wb"
        ).write(dataInput)
        open(
            os.path.join(util.getHackDataFolderPath(currentErrorCount), "answer"), "wb"
        ).write(dataAnswer)
        open(
            os.path.join(util.getHackDataFolderPath(currentErrorCount), "output"), "wb"
        ).write(dataOutput)
        logger.info(f"[autohack thread#{threadId}] {logMessage}")
        updateThreadStatus(threadId, message)

    def processData(threadId: int) -> None:
        global dataCount, errorDataCount

        while True:
            # Get next data count
            with dataCountLock:
                if dataCount >= config.getConfigEntry(
                    "maximum_number_of_data"
                ) or errorDataCount >= config.getConfigEntry("error_data_number_limit"):
                    break
                dataCount += 1
                currentDataCount = dataCount

            try:
                logger.info(
                    f"[autohack thread#{threadId}] Generating data {currentDataCount}."
                )
                updateThreadStatus(threadId, f"{currentDataCount}: Generate input.")
                dataInput = function.generateInput(generateCommand, clientID)
            except exception.InputGenerationError as e:
                logger.error(
                    f"[autohack thread#{threadId}] Input generation failed: {e}"
                )
                updateThreadStatus(threadId, f"Error: {e}")
                continue

            try:
                logger.info(
                    f"[autohack thread#{threadId}] Generating answer for data {currentDataCount}."
                )
                updateThreadStatus(threadId, f"{currentDataCount}: Generate answer.")
                dataAnswer = function.generateAnswer(
                    stdCommand,
                    dataInput,
                    clientID,
                )
            except exception.AnswerGenerationError as e:
                logger.error(
                    f"[autohack thread#{threadId}] Answer generation failed: {e}"
                )
                updateThreadStatus(threadId, f"Error: {e}")
                continue

            logger.info(
                f"[autohack thread#{threadId}] Run source code for data {currentDataCount}."
            )
            updateThreadStatus(threadId, f"{currentDataCount}: Run source code.")
            result = function.runSourceCode(
                sourceCommand, dataInput, timeLimit, memoryLimit
            )

            stdout = result.stdout if result.stdout is not None else b""

            if result.memoryOut:
                saveErrorData(
                    dataInput,
                    dataAnswer,
                    stdout,
                    f"Memory limit exceeded for data {currentDataCount}.",
                    f"Memory limit exceeded for data {currentDataCount}.",
                    threadId,
                )
                continue
            elif result.timeOut:
                saveErrorData(
                    dataInput,
                    dataAnswer,
                    stdout,
                    f"Time limit exceeded for data {currentDataCount}.",
                    f"Time limit exceeded for data {currentDataCount}.",
                    threadId,
                )
                continue
            elif result.returnCode != 0:
                saveErrorData(
                    dataInput,
                    dataAnswer,
                    stdout,
                    f"Runtime error for data {currentDataCount} (code {result.returnCode}).",
                    f"Runtime error for data {currentDataCount} with return code {result.returnCode}.",
                    threadId,
                )
                continue

            checkerResult = checker.basicChecker(stdout, dataAnswer)
            if not checkerResult[0]:
                saveErrorData(
                    dataInput,
                    dataAnswer,
                    stdout,
                    f"Wrong answer for data {currentDataCount}. {checkerResult[1]}",
                    f"Wrong answer for data {currentDataCount}. Checker output: {checkerResult[1]}",
                    threadId,
                )
            else:
                updateThreadStatus(threadId, f"{currentDataCount}: Accepted.")

        updateThreadStatus(threadId, "Finished.")

    # Start threads
    with ThreadPoolExecutor(max_workers=threadCount) as executor:
        futures = [executor.submit(processData, i + 1) for i in range(threadCount)]

        # Wait for all threads to complete
        for future in futures:
            future.result()

    # Print final result below thread status lines
    print()
    end = time.time()
    print(end - start)
    print(f"Finished. {dataCount} data generated, {errorDataCount} error data found.")
