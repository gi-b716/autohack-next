from .constant import *
from . import exception, function, checker, config, logger, util
from .i18n import _, setup_i18n
import logging, shutil, uuid, os

if __name__ == "__main__":
    # Initialize internationalization
    setup_i18n()

    util.checkDirectoryExists(DATA_FOLDER_PATH)
    util.checkDirectoryExists(LOG_FOLDER_PATH)
    util.checkDirectoryExists(TEMP_FOLDER_PATH)
    if util.mswindows():
        os.system("attrib +h {0}".format(DATA_FOLDER_PATH))

    # TODO Remember to delete DEBUG tag
    logger = logger.Logger(LOG_FOLDER_PATH, logging.WARNING).getLogger()
    config = config.Config(CONFIG_FILE_PATH, logger)
    logger.info(_('Data folder path: "{0}"').format(DATA_FOLDER_PATH))
    clientID = str(uuid.uuid4())
    logger.info(_("Client ID: {0}").format(clientID))
    logger.info(_("Initialized."))

    if os.path.exists(HACK_DATA_FOLDER_PATH):
        shutil.rmtree(HACK_DATA_FOLDER_PATH)

    fileList = [
        [config.getConfigEntry("commands.compile.source"), "source code"],
        [config.getConfigEntry("commands.compile.std"), "standard code"],
        [config.getConfigEntry("commands.compile.generator"), "generator code"],
    ]
    for file in fileList:
        print(f"\x1b[1K\r{_('Compile {0}.').format(file[1])}", end="")
        try:
            function.compileCode(file[0], file[1])
        except exception.CompilationError as e:
            logger.error(
                _("{0} compilation failed: {1}").format(e.fileName.capitalize(), e)
            )
            print(f"\r{e}")
            exit(1)
        else:
            logger.info(_("{0} compiled successfully.").format(file[1].capitalize()))
    print(f"\x1b[1K\r{_('Compile finished.')}")

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
            logger.info(_("Generating data {0}.").format(dataCount))
            print(f"\x1b[1K\r{_('{0}: Generate input.').format(dataCount)}", end="")
            dataInput = function.generateInput(generateCommand, clientID)
        except exception.InputGenerationError as e:
            logger.error(_("Input generation failed: {0}").format(e))
            print(f"\x1b[1K\r{e}")
            exit(1)

        try:
            logger.info(_("Generating answer for data {0}.").format(dataCount))
            print(f"\x1b[1K\r{_('{0}: Generate answer.').format(dataCount)}", end="")
            dataAnswer = function.generateAnswer(
                stdCommand,
                dataInput,
                clientID,
            )
        except exception.AnswerGenerationError as e:
            logger.error(_("Answer generation failed: {0}").format(e))
            print(f"\x1b[1K\r{e}")
            exit(1)

        logger.info(_("Run source code for data {0}.").format(dataCount))
        print(f"\x1b[1K\r{_('{0}: Run source code.').format(dataCount)}", end="")
        result = function.runSourceCode(
            sourceCommand, dataInput, timeLimit, memoryLimit
        )

        stdout = result.stdout if result.stdout is not None else b""

        if result.memoryOut:
            saveErrorData(
                dataInput,
                dataAnswer,
                stdout,
                f"\x1b[1K\r{_('Memory limit exceeded for data {0}. Hack data saved to {1}.').format(dataCount, util.getHackDataFolderPath(errorDataCount))}",
                _("Memory limit exceeded for data {0}.").format(dataCount),
            )
            continue
        elif result.timeOut:
            saveErrorData(
                dataInput,
                dataAnswer,
                stdout,
                f"\x1b[1K\r{_('Time limit exceeded for data {0}. Hack data saved to {1}.').format(dataCount, util.getHackDataFolderPath(errorDataCount))}",
                _("Time limit exceeded for data {0}.").format(dataCount),
            )
            continue
        elif result.returnCode != 0:
            saveErrorData(
                dataInput,
                dataAnswer,
                stdout,
                f"\x1b[1K\r{_('Runtime error for data {0} with return code {1}. Hack data saved to {2}.').format(dataCount, result.returnCode, util.getHackDataFolderPath(errorDataCount))}",
                _("Runtime error for data {0} with return code {1}.").format(
                    dataCount, result.returnCode
                ),
            )
            continue

        checkerResult = checker.basicChecker(stdout, dataAnswer)
        if not checkerResult[0]:
            saveErrorData(
                dataInput,
                dataAnswer,
                stdout,
                f"\x1b[1K\r{_('Wrong answer for data {0}. Hack data saved to {1}. Checker output: {2}').format(dataCount, util.getHackDataFolderPath(errorDataCount), checkerResult[1])}",
                _("Wrong answer for data {0}. Checker output: {1}").format(
                    dataCount, checkerResult[1]
                ),
            )

    print(
        f"\x1b[1K\r{_('Finished. {0} data generated, {1} error data found.').format(dataCount, errorDataCount)}"
    )
