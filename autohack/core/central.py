import locale
import os
import time
import traceback

from autohack import __VERSION__
from autohack.core.build import BUILD_COMMIT_HASH
from autohack.core.constant import AUTO_DETECT_LANG_SENTINEL, DEFAULT_LANGUAGE_ID, LANGUAGE_MAPS, SYSTEM_LOCALE_TO_LANG
from autohack.core.exception import autohackRuntimeError
from autohack.core.lib.config import loadConfig, saveConfig
from autohack.core.lib.i18n import I18N
from autohack.core.lib.logger import Logger
from autohack.core.model import ConfigRoot, GlobalConfigRoot
from autohack.core.path import (
    CHECKER_FOLDER_PATH,
    CONFIG_FILE_PATH,
    DATA_FOLDER_PATH,
    GLOBAL_CONFIG_FILE_PATH,
    HACK_DATA_STORAGE_FOLDER_PATH,
    LOG_FOLDER_PATH,
    TRANSLATION_FOLDER_PATH,
    getExportDataPath,
    getExportFolderPath,
    getHackDataFilePath,
    getHackDataStorageFolderPath,
)
from autohack.core.plugin.checker import (
    checkerType,
    deactivateType,
    emptyDeactivate,
    getChecker,
)
from autohack.core.util.ansi import ANSIHelper
from autohack.core.util.console import (
    hideCursor,
    selectionMenu,
    write,
    writeMessage,
)
from autohack.core.util.fs import ensureDirExists, getFolderSize, writeData
from autohack.core.util.run import (
    compileCode,
    generateAnswer,
    generateInput,
    runSourceCode,
)
from autohack.core.util.system import exitProgram


class AppCentral:
    def __init__(self, clientID: str, logTime: time.struct_time, debug: bool = False) -> None:
        self.clientID = clientID
        self.logTime = logTime
        self.debug = debug

    def run(self) -> None:
        hideCursor()

        ensureDirExists(CHECKER_FOLDER_PATH)
        ensureDirExists(LOG_FOLDER_PATH)

        Logger(LOG_FOLDER_PATH, self.debug)
        logger = Logger.getBindLogger("autohack")

        I18n = I18N(TRANSLATION_FOLDER_PATH)
        _ = I18n.translate

        if not GLOBAL_CONFIG_FILE_PATH.exists():
            logger.info("Global config file not found. Creating new one.")
            write("Welcome to autohack-next!", endl=1)
            write("A global config file will be created.", endl=1)
            write("Please select your preferred language:", endl=1)

            langMenuItems: list[str] = []
            langMenuValues: list[str] = []

            systemLang, _encoding = locale.getdefaultlocale()
            autoDetectedLang: str | None = None
            if systemLang:
                for sysLocale, autoLangID in SYSTEM_LOCALE_TO_LANG.items():
                    if systemLang.startswith(sysLocale):
                        autoDetectedLang = autoLangID
                        break

            if autoDetectedLang is not None:
                autoLabel = I18n.translate("Auto Detect", language=autoDetectedLang)
                langInfo = I18n.translate("English (US)", language=autoDetectedLang)
                langMenuItems.append(f"{autoLabel} ({langInfo})")
                langMenuValues.append(AUTO_DETECT_LANG_SENTINEL)

            langMenuItems.extend([f"{langID} / {I18n.translate('English (US)', language=langID)}" for langID in LANGUAGE_MAPS])
            langMenuValues.extend(LANGUAGE_MAPS)

            selectedLangIndex = selectionMenu(langMenuItems)
            selectedLang = langMenuValues[selectedLangIndex]
            if selectedLang == AUTO_DETECT_LANG_SENTINEL:
                selectedLang = autoDetectedLang
            GlobalConfigRoot.language.value = selectedLang
            saveConfig(GLOBAL_CONFIG_FILE_PATH, GlobalConfigRoot)
            I18n.setDefaultLanguage(selectedLang)
            write(ANSIHelper.clearLine())
            write(ANSIHelper.prevLine())
            write(ANSIHelper.clearLine())
            write(ANSIHelper.prevLine())
            write(ANSIHelper.clearLine())
            writeMessage(
                _("You selected: {}", _("English (US)")),
                endl=1,
            )
            writeMessage(
                _(
                    "You can change this later in the global config file on {}",
                    str(GLOBAL_CONFIG_FILE_PATH),
                ),
                endl=2,
            )

        loadConfig(GLOBAL_CONFIG_FILE_PATH, GlobalConfigRoot)
        I18n.setDefaultLanguage(GlobalConfigRoot.language.value)

        firstTime = not CONFIG_FILE_PATH.exists()
        loadConfig(CONFIG_FILE_PATH, ConfigRoot)
        if firstTime:
            writeMessage(_("Config file created at {}", str(CONFIG_FILE_PATH)))
            exitProgram()

        logger.info(f'Data folder path: "{DATA_FOLDER_PATH}"')
        logger.info(f"Client ID: {self.clientID}")
        logger.info(f"Initialized. Version: {__VERSION__}")
        writeMessage(
            _("autohack-next {} ({}) - Client ID: {}", __VERSION__, BUILD_COMMIT_HASH, self.clientID),
            endl=2,
        )
        writeMessage(
            _("Hack data storaged to {}", str(getHackDataStorageFolderPath(self.clientID, self.logTime))),
            endl=1,
        )
        writeMessage(
            _("Log file: {}", str(LOG_FOLDER_PATH / "latest.log")),
            endl=1,
        )
        writeMessage(
            _("Error export to {}", str(getExportFolderPath(self.logTime, self.clientID))),
            endl=1,
        )
        writeMessage(
            _("Custom checker folder: {}", str(CHECKER_FOLDER_PATH)),
            endl=2,
        )

        waitTimeBeforeStart = GlobalConfigRoot.wait_time_before_start.value
        for i in range(waitTimeBeforeStart, 0, -1):
            writeMessage(_("Starting in {} seconds...", i), clear=True)
            time.sleep(1)

        fileList = [
            [
                ConfigRoot.commands.compile.source.value,
                "source code",
            ],
            [
                ConfigRoot.commands.compile.std.value,
                "standard code",
            ],
            [
                ConfigRoot.commands.compile.generator.value,
                "generator code",
            ],
        ]
        for file in fileList:
            writeMessage(
                _("Compile {}.", _(file[1])),
                clear=True,
            )
            try:
                compileCode(file[0])
            except autohackRuntimeError as e:
                logger.error(
                    f"{_(file[1], language=DEFAULT_LANGUAGE_ID).capitalize()} compilation failed with return code {e.returnCode} and message:\n{e.output.decode(errors='ignore')}"
                )
                writeMessage(
                    _("{} compilation failed with return code {}.", _(file[1]).capitalize(), str(e.returnCode)),
                    endl=2,
                    clear=True,
                    highlight=True,
                )
                write(e.output.decode(errors="ignore"))
                exitProgram(1)
            else:
                logger.debug(f"{_(file[1], language=DEFAULT_LANGUAGE_ID).capitalize()} compiled successfully.")
        writeMessage(
            _("Compile finished."),
            endl=1,
            clear=True,
        )

        writeMessage(_('Activating checker "{}"...', ConfigRoot.checker.name.value))

        def _defaultChecker(inp: bytes, out: bytes, ans: bytes, args: dict) -> tuple[bool, str]:
            return (
                False,
                _("No checker activated."),
            )

        currentChecker: checkerType = _defaultChecker
        deactivateFunc: deactivateType = emptyDeactivate
        try:
            getCheckerResult = getChecker(
                CHECKER_FOLDER_PATH,
                ConfigRoot.checker.name.value,
                ConfigRoot.checker.args.value,
            )
            currentChecker = getCheckerResult[0]
            deactivateFunc = getCheckerResult[1]
        except Exception as e:
            logger.critical(f"{e}")
            writeMessage(
                _("Checker activation failed."),
                endl=1,
                clear=True,
                highlight=True,
            )
            traceback.print_exc()
            exitProgram(1)
        writeMessage(
            _('Checker "{}" activated.', ConfigRoot.checker.name.value),
            endl=2,
            clear=True,
        )

        dataCount, errorDataCount = 0, 0
        lastStatusError = False
        generateCommand = ConfigRoot.commands.run.generator.value
        stdCommand = ConfigRoot.commands.run.std.value
        sourceCommand = ConfigRoot.commands.run.source.value
        timeLimit = ConfigRoot.time_limit.value / 1000
        memoryLimit = ConfigRoot.memory_limit.value * 1024 * 1024
        inputFilePath = ConfigRoot.paths.input.value
        answerFilePath = ConfigRoot.paths.answer.value
        outputFilePath = ConfigRoot.paths.output.value
        maximumDataLimit = ConfigRoot.maximum_number_of_data.value
        errorDataLimit = ConfigRoot.error_data_number_limit.value
        refreshSpeed = GlobalConfigRoot.refresh_speed.value
        checkerArgs = ConfigRoot.checker.args.value

        timeLimit = None if timeLimit == 0 else timeLimit
        memoryLimit = None if memoryLimit == 0 else memoryLimit

        def updateStatus(
            total: float,
            averagePerS: float,
            averagePerData: float,
            addtional: str,
        ) -> None:
            # write(
            #     f"Time taken: {total:.2f} seconds, average {averagePerS:.2f} data per second, {averagePerData:.2f} second per data.{addtional}",
            #     clear=True,
            # )
            writeMessage(
                _(
                    "Time taken: {} seconds, average {} data per second, {} second per data.",
                    f"{total:.2f}",
                    f"{averagePerS:.2f}",
                    f"{averagePerData:.2f}",
                ),
                clear=True,
            )
            write(addtional)

        write(endl=1)
        updateStatus(0.0, 0.0, 0.0, " (0%)" if maximumDataLimit > 0 else "")
        write(ANSIHelper.prevLine())

        startTime = time.time()

        while (maximumDataLimit <= 0 or dataCount < maximumDataLimit) and (errorDataLimit <= 0 or errorDataCount < errorDataLimit):
            dataInput = b""
            dataAnswer = b""

            dataCount += 1

            try:
                # write(f"{dataCount}: Generate input.", clear=True)
                writeMessage(
                    _("{}: Generate input.", str(dataCount)),
                    clear=True,
                )
                logger.debug(f"Generating data {dataCount}.")
                dataInput = generateInput(generateCommand)
            except autohackRuntimeError as e:
                logger.error(f"Input generation failed with return code {e.returnCode}.")
                writeMessage(
                    _("Input generation failed with return code {}.", str(e.returnCode)),
                    endl=1,
                    clear=True,
                    highlight=True,
                )
                inputExportPath = getExportDataPath(getExportFolderPath(self.logTime, self.clientID), "input")
                writeData(inputExportPath, e.output)
                writeMessage(
                    _("Input data saved to {}", str(inputExportPath)),
                    clear=True,
                )
                exitProgram(1)

            try:
                # write(f"{dataCount}: Generate answer.", clear=True)
                writeMessage(
                    _("{}: Generate answer.", str(dataCount)),
                    clear=True,
                )
                logger.debug(f"Generating answer for data {dataCount}.")
                dataAnswer = generateAnswer(stdCommand, dataInput)
            except autohackRuntimeError as e:
                logger.error(f"Answer generation failed with return code {e.returnCode}.")
                writeMessage(
                    _("Answer generation failed with return code {}.", str(e.returnCode)),
                    endl=1,
                    clear=True,
                    highlight=True,
                )
                inputExportPath = getExportDataPath(getExportFolderPath(self.logTime, self.clientID), "input")
                writeData(inputExportPath, dataInput)
                writeMessage(
                    _("Input data saved to {}", str(inputExportPath)),
                    endl=1,
                    clear=True,
                )
                answerExportPath = getExportDataPath(getExportFolderPath(self.logTime, self.clientID), "answer")
                writeData(answerExportPath, e.output)
                writeMessage(
                    _("Answer data saved to {}", str(answerExportPath)),
                    clear=True,
                )
                exitProgram(1)

            # write(f"{dataCount}: Run source code.", clear=True)
            writeMessage(
                _("{}: Run source code.", str(dataCount)),
                clear=True,
            )
            logger.debug(f"Run source code for data {dataCount}.")
            result = runSourceCode(sourceCommand, dataInput, timeLimit, memoryLimit)
            if result.stdout is None:
                result.stdout = b""
            if result.stderr is None:
                result.stderr = b""

            # TODO: Refresh when running exe. Use threading or async?
            if dataCount % refreshSpeed == 0 or lastStatusError:
                lastStatusError = False
                currentTime = time.time()
                write(endl=1)
                # write(
                #     f"Time taken: {currentTime - startTime:.2f} seconds, average {dataCount/(currentTime - startTime):.2f} data per second, {(currentTime - startTime)/dataCount:.2f} second per data.{f" ({dataCount*100/maximumDataLimit:.0f}%)" if maximumDataLimit > 0 else ""}",
                #     clear=True,
                # )
                updateStatus(
                    currentTime - startTime,
                    dataCount / (currentTime - startTime),
                    (currentTime - startTime) / dataCount,
                    f" ({dataCount * 100 / maximumDataLimit:.0f}%)" if maximumDataLimit > 0 else "",
                )
                write(ANSIHelper.prevLine())

            saveData, termMessage, logMessage, extMessage, exitAfterSave = (
                False,
                "",
                "",
                None,
                False,
            )

            if result.memoryOut:
                saveData = True
                logMessage = f"Memory limit exceeded for data {dataCount}."
                termMessage = _("Memory limit exceeded for data {}.", str(dataCount))
                if result.maxMemory is not None:
                    extMessage = _("Max {} MB.", f"{result.maxMemory / 1024 / 1024:.4f}")
            elif result.timeOut:
                saveData = True
                logMessage = f"Time limit exceeded for data {dataCount}."
                termMessage = _("Time limit exceeded for data {}.", str(dataCount))
                if result.totalTime is not None:
                    extMessage = _("Truncated at {} ms.", f"{result.totalTime * 1000:.4f}")
            elif result.returnCode != 0:
                saveData = True
                logMessage = f"Runtime error for data {dataCount} with return code {result.returnCode}."
                termMessage = _("Runtime error for data {}.", str(dataCount))
                if result.returnCode is not None:
                    extMessage = _("Return code: {}", str(result.returnCode))

            checkerResult = (False, _("Checker not executed."))
            try:
                checkerResult = currentChecker(dataInput, result.stdout, dataAnswer, checkerArgs)
            except Exception as e:
                saveData = True
                termMessage = _("Checker error for data {}.", str(dataCount))
                logMessage = f"Checker error for data {dataCount}. Exception: {e}"
                extMessage = f"{_('Traceback:')}\n{traceback.format_exc()}"
                checkerResult = (
                    False,
                    _("Checker exception occurred."),
                )
                exitAfterSave = True

            if not saveData and not checkerResult[0]:
                saveData = True
                termMessage = _("Wrong answer for data {}.", str(dataCount))
                logMessage = f"Wrong answer for data {dataCount}. Checker output: {checkerResult[1]}"
                extMessage = checkerResult[1]

            if saveData:
                lastStatusError = True
                errorDataCount += 1
                writeData(
                    getHackDataFilePath(
                        getHackDataStorageFolderPath(self.clientID, self.logTime),
                        errorDataCount,
                        inputFilePath,
                    ),
                    dataInput,
                )
                writeData(
                    getHackDataFilePath(
                        getHackDataStorageFolderPath(self.clientID, self.logTime),
                        errorDataCount,
                        answerFilePath,
                    ),
                    dataAnswer,
                )
                writeData(
                    getHackDataFilePath(
                        getHackDataStorageFolderPath(self.clientID, self.logTime),
                        errorDataCount,
                        outputFilePath,
                    ),
                    result.stdout,
                )
                write(f"[{errorDataCount}]: {termMessage}", endl=1, clear=True)
                if extMessage is not None and extMessage != "":
                    write(
                        f"{(len(f'[{errorDataCount}]: ') - 3) * ' '} - {extMessage}",
                        endl=1,
                        clear=True,
                    )
                logger.info(f"{logMessage}")

            if exitAfterSave:
                writeMessage(
                    _("Exiting due to checker exception."),
                    clear=True,
                    highlight=True,
                )
                exitProgram(0)

        endTime = time.time()

        writeMessage(
            _("Finished. {} data generated, {} error data found.", str(dataCount), str(errorDataCount)),
            endl=1,
            clear=True,
        )
        # write(
        #     f"Time taken: {endTime - startTime:.2f} seconds, average {dataCount/(endTime - startTime):.2f} data per second, {(endTime - startTime)/dataCount:.2f} second per data.",
        #     2,
        #     True,
        # )
        updateStatus(
            endTime - startTime,
            dataCount / (endTime - startTime),
            (endTime - startTime) / dataCount,
            "",
        )
        write(endl=2)

        # if errorDataCount == 0:
        #     shutil.rmtree(getHackDataStorageFolderPath(clientID))
        #     write("No error data found. Hack data folder removed.", 1)
        #     logger.info("No error data found. Hack data folder removed.")

        dataFolderMaxSize = GlobalConfigRoot.data_folder_max_size.value
        # print(getFolderSize(HACK_DATA_STORAGE_FOLDER_PATH) / 1024 / 1024, " ", dataFolderMaxSize)
        if HACK_DATA_STORAGE_FOLDER_PATH.exists() and getFolderSize(HACK_DATA_STORAGE_FOLDER_PATH) > dataFolderMaxSize * 1024 * 1024:
            logger.warning(f"Hack data storage folder size exceeds {dataFolderMaxSize} MB: {HACK_DATA_STORAGE_FOLDER_PATH}")
            # write(f"Warning: Hack data storage folder size exceeds {DATA_FOLDER_MAX_SIZE} MB: {HACK_DATA_STORAGE_FOLDER_PATH}", 2)
            writeMessage(
                _("Warning: Hack data storage folder size exceeds {} MB: {}", str(dataFolderMaxSize), str(HACK_DATA_STORAGE_FOLDER_PATH)),
                endl=2,
                highlight=True,
            )

        writeMessage(_("Deactivating checker..."))
        try:
            deactivateFunc(ConfigRoot.checker.args.value)
        except Exception as e:
            logger.error(f"Checker deactivation failed with exception: {e}")
            writeMessage(
                _("Checker deactivation failed."),
                endl=1,
                clear=True,
                highlight=True,
            )
            traceback.print_exc()
            exitProgram(1)
        writeMessage(
            _("Checker deactivated."),
            endl=1,
            clear=True,
        )

        writeMessage(_("Executing post process command."), endl=1)
        os.system(ConfigRoot.command_at_end.value)
        logger.info("Finished.")
