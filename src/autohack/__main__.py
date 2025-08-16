try:
    from autohack.core.constant import *
    from autohack.core.exception import *
    from autohack.core.path import *
    from autohack.core.util import *
    from autohack.lib.config import *
    from autohack.lib.logger import *
    from autohack.checker import *
    from autohack.function import *
    import argparse, logging, shutil, time, uuid, sys, os

    if __name__ == "__main__" or os.getenv("AUTOHACK_ENTRYPOINT", "0") == "1":
        # Hide cursor
        # https://www.cnblogs.com/chargedcreeper/p/-/ANSI
        sys.stdout.write("\x1b[?25l")

        parser = argparse.ArgumentParser(
            prog="autohack", description="autohack-next - Automated hack data generator"
        )
        parser.add_argument(
            "--version", action="store_true", help="Show version information"
        )
        parser.add_argument("--version-id", action="store_true", help="Show version ID")
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug mode with DEBUG logging level",
        )

        args = parser.parse_args()

        if args.version:
            sys.stdout.write(f"{VERSION}\n")
            sys.exit(0)

        if args.version_id:
            sys.stdout.write(f"{VERSION_ID}\n")
            sys.exit(0)

        if args.debug:
            sys.stdout.write("Debug mode enabled. Logging level set to DEBUG.\n")

        checkDirectoryExists(DATA_FOLDER_PATH)
        checkDirectoryExists(LOG_FOLDER_PATH)
        checkDirectoryExists(TEMP_FOLDER_PATH)
        if mswindows():
            os.system("attrib +h {0}".format(DATA_FOLDER_PATH))

        loggerObject = Logger(
            LOG_FOLDER_PATH,
            logging.DEBUG if args.debug else logging.INFO,
        )
        logger = loggerObject.getLogger()
        config = Config(CONFIG_FILE_PATH, logger)
        logger.info(f'[autohack] Data folder path: "{DATA_FOLDER_PATH}"')
        clientID = str(uuid.uuid4())
        logger.info(f"[autohack] Client ID: {clientID}")
        sys.stdout.write(f"autohack-next {VERSION} - Client ID: {clientID}\n")
        logger.info(f"[autohack] Initialized. Version: {VERSION}")

        symlinkFallback = False

        sys.stdout.write("\n")
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
            sys.stdout.write(
                "Hack data folder symlink creation failed. Using fallback method.\n"
            )
            logger.warning("[autohack] Symlink creation failed. Using fallback method.")
            checkDirectoryExists(CURRENT_HACK_DATA_FOLDER_PATH)
        sys.stdout.write(
            f"Hack data storaged to {CURRENT_HACK_DATA_FOLDER_PATH}.\n{' '*18}and {getHackDataStorageFolderPath(clientID)}\nLog file: {loggerObject.getLogFilePath()}\n"
        )

        sys.stdout.write("\n")
        for i in range(3):
            sys.stdout.write(f"\x1b[1K\rStarting in {3-i} seconds...")
            time.sleep(1)

        fileList = [
            [config.getConfigEntry("commands.compile.source"), "source code"],
            [config.getConfigEntry("commands.compile.std"), "standard code"],
            [config.getConfigEntry("commands.compile.generator"), "generator code"],
        ]
        for file in fileList:
            sys.stdout.write(f"\x1b[1K\rCompile {file[1]}.")
            try:
                compileCode(file[0], file[1])
            except CompilationError as e:
                logger.error(
                    f"[autohack] {e.fileName.capitalize()} compilation failed: {e}"
                )
                sys.stdout.write(f"\r{e}\n")
                exit(1)
            else:
                logger.debug(
                    f"[autohack] {file[1].capitalize()} compiled successfully."
                )
        sys.stdout.write("\x1b[1K\rCompile finished.\n")

        dataCount, errorDataCount = 0, 0
        generateCommand = config.getConfigEntry("commands.run.generator")
        stdCommand = config.getConfigEntry("commands.run.std")
        sourceCommand = config.getConfigEntry("commands.run.source")
        timeLimit = config.getConfigEntry("time_limit")
        memoryLimit = config.getConfigEntry("memory_limit") * 1024 * 1024
        inputFilePath = config.getConfigEntry("paths.input")
        answerFilePath = config.getConfigEntry("paths.answer")
        outputFilePath = config.getConfigEntry("paths.output")
        maximumDataLimit = config.getConfigEntry("maximum_number_of_data")
        errorDataLimit = config.getConfigEntry("error_data_number_limit")
        refreshSpeed = config.getConfigEntry("refresh_speed")

        lastStatusError = False

        def saveErrorData(
            dataInput: bytes,
            dataAnswer: bytes,
            dataOutput: bytes,
            message: str,
            logMessage: str,
        ) -> None:
            global lastStatusError, errorDataCount, logger
            lastStatusError = True
            errorDataCount += 1
            checkDirectoryExists(getHackDataFolderPath(errorDataCount, inputFilePath))
            checkDirectoryExists(getHackDataFolderPath(errorDataCount, answerFilePath))
            checkDirectoryExists(getHackDataFolderPath(errorDataCount, outputFilePath))
            open(getHackDataFilePath(errorDataCount, inputFilePath), "wb").write(
                dataInput
            )
            open(getHackDataFilePath(errorDataCount, answerFilePath), "wb").write(
                dataAnswer
            )
            open(getHackDataFilePath(errorDataCount, outputFilePath), "wb").write(
                dataOutput
            )
            logger.info(logMessage)
            sys.stdout.write(f"{message}\n")

        startTime = time.time()

        sys.stdout.write("\n")
        while (maximumDataLimit <= 0 or dataCount < maximumDataLimit) and (
            errorDataLimit <= 0 or errorDataCount < errorDataLimit
        ):
            dataCount += 1

            try:
                logger.debug(f"[autohack] Generating data {dataCount}.")
                sys.stdout.write(f"\x1b[2K\r{dataCount}: Generate input.")
                dataInput = generateInput(generateCommand, clientID)
            except InputGenerationError as e:
                logger.error(f"[autohack] Input generation failed: {e}")
                sys.stdout.write(f"\x1b[2K\r{e}\n")
                exit(1)

            try:
                logger.debug(f"[autohack] Generating answer for data {dataCount}.")
                sys.stdout.write(f"\x1b[2K\r{dataCount}: Generate answer.")
                dataAnswer = generateAnswer(
                    stdCommand,
                    dataInput,
                    clientID,
                )
            except AnswerGenerationError as e:
                logger.error(f"[autohack] Answer generation failed: {e}")
                sys.stdout.write(f"\x1b[2K\r{e}\n")
                exit(1)

            logger.debug(f"[autohack] Run source code for data {dataCount}.")
            sys.stdout.write(f"\x1b[2K\r{dataCount}: Run source code.")
            result = runSourceCode(sourceCommand, dataInput, timeLimit, memoryLimit)

            # TODO: Refresh when running exe. Use threading or async?
            if dataCount % refreshSpeed == 0 or lastStatusError:
                lastStatusError = False
                currentTime = time.time()
                sys.stdout.write(
                    f"\n\x1b[2K\rTime taken: {currentTime - startTime:.2f} seconds, average {dataCount/(currentTime - startTime):.2f} data per second, {(currentTime - startTime)/dataCount:.2f} second per data.{f" (%{dataCount*100/maximumDataLimit:.0f})" if maximumDataLimit > 0 else ""}\x1b[1A"
                )

            if result.memoryOut:
                saveErrorData(
                    dataInput,
                    dataAnswer,
                    result.stdout,
                    f"\x1b[2K\r[{errorDataCount+1}]: Memory limit exceeded for data {dataCount}.",
                    f"[autohack] Memory limit exceeded for data {dataCount}.",
                )
                continue
            elif result.timeOut:
                saveErrorData(
                    dataInput,
                    dataAnswer,
                    result.stdout,
                    f"\x1b[2K\r[{errorDataCount+1}]: Time limit exceeded for data {dataCount}.",
                    f"[autohack] Time limit exceeded for data {dataCount}.",
                )
                continue
            elif result.returnCode != 0:
                saveErrorData(
                    dataInput,
                    dataAnswer,
                    result.stdout,
                    f"\x1b[2K\r[{errorDataCount+1}]: Runtime error for data {dataCount} with return code {result.returnCode}.",
                    f"[autohack] Runtime error for data {dataCount} with return code {result.returnCode}.",
                )
                continue

            checkerResult = basicChecker(result.stdout, dataAnswer)
            if not checkerResult[0]:
                saveErrorData(
                    dataInput,
                    dataAnswer,
                    result.stdout,
                    f"\x1b[2K\r[{errorDataCount+1}]: Wrong answer for data {dataCount}.\n\x1b[2K\r{(len(f"[{errorDataCount+1}]: ")-3)*' '} - {checkerResult[1]}",
                    f"[autohack] Wrong answer for data {dataCount}. Checker output: {checkerResult[1]}",
                )

        endTime = time.time()

        sys.stdout.write(
            f"\x1b[2K\rFinished. {dataCount} data generated, {errorDataCount} error data found.\n\x1b[2K\rTime taken: {endTime - startTime:.2f} seconds, average {dataCount/(endTime - startTime):.2f} data per second, {(endTime - startTime)/dataCount:.2f} second per data.\n"
        )
        if errorDataCount > 0:
            if symlinkFallback:
                sys.stdout.write(f"Saving hack data to data storage folder...")
                shutil.copytree(
                    CURRENT_HACK_DATA_FOLDER_PATH,
                    getHackDataStorageFolderPath(clientID),
                    dirs_exist_ok=True,
                )
                sys.stdout.write("\x1b[1K\rHack data saved to data storage folder.\n")
                logger.info(
                    f"[autohack] Hack data saved to data storage folder: {getHackDataStorageFolderPath(clientID)}"
                )
        else:
            shutil.rmtree(getHackDataStorageFolderPath(clientID))
            sys.stdout.write("No error data found. Hack data folder removed.\n")
            logger.info("[autohack] No error data found. Hack data folder removed.")
        if (
            os.path.exists(HACK_DATA_STORAGE_FOLDER_PATH)
            and os.path.getsize(HACK_DATA_STORAGE_FOLDER_PATH) > 256 * 1024 * 1024
        ):
            logger.warning(
                f"[autohack] Hack data storage folder size exceeds 256 MB: {HACK_DATA_STORAGE_FOLDER_PATH}"
            )
            sys.stdout.write(
                f"Warning: Hack data storage folder size exceeds 256 MB: {HACK_DATA_STORAGE_FOLDER_PATH}\n"
            )

        comment = input("\nComment (optional): \x1b[?25h")
        sys.stdout.write("\x1b[?25l")
        open(RECORD_FILE_PATH, "a+").write(
            f"{time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))} / {clientID}\n{dataCount} data generated, {errorDataCount} error data found.\nTime taken: {endTime - startTime:.2f} seconds, average {dataCount/(endTime - startTime):.2f} data per second, {(endTime - startTime)/dataCount:.2f} second per data.\n{comment}\n\n"
        )
        sys.stdout.write(f"Record saved to {RECORD_FILE_PATH}.\n")
        logger.info(f"[autohack] Record saved to {RECORD_FILE_PATH}.")

except KeyboardInterrupt:
    import sys

    sys.stdout.write("\x1b[1;31mProcess interrupted by user.\n")
    sys.exit(0)
except Exception as e:
    import traceback, time, os

    sys.stdout.write(f"\x1b[1;31mUnhandled exception.\n")
    errorFilePath = os.path.join(os.getcwd(), f"autohack-error.{time.time():.0f}.log")
    open(errorFilePath, "w+").write(repr(e))
    sys.stdout.write(f"\x1b[1;31mError details saved to {errorFilePath}.\x1b[0m\n\n")
    # logger.critical(f"[autohack] Unhandled exception: {e.__str__()}")
    traceback.print_exc()
