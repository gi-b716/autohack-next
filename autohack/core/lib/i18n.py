import os
import pathlib

import json5

from autohack.core.constant import DEFAULT_LANGUAGE_ID
from autohack.core.lib.logger import Logger


class I18N:
    def __init__(
        self,
        translationFileDir: pathlib.Path,
    ) -> None:
        self.translationFileDir = translationFileDir
        self.logger = Logger.getBindLogger("i18n")
        self.translations = {}
        self.setDefaultLanguage(DEFAULT_LANGUAGE_ID)

    def setDefaultLanguage(self, language: str) -> None:
        self.logger.info(f'Default language: "{language}"')
        self.defaultLanguage = language
        if language not in self.translations:
            self.loadTranslation(language)

    def loadTranslation(self, language: str) -> None:
        self.translationFile = self.translationFileDir / f"{language}.json"
        self.logger.info(f'Translation file: "{self.translationFile}"')
        self.translations[language] = self.loadTranslationFile(self.translationFile)

    def loadTranslationFile(self, filePath: pathlib.Path) -> dict[str, str]:
        if not os.path.exists(filePath):
            self.logger.critical("Translation file not found.")
            raise FileNotFoundError(f"Translation file {filePath} not found.")
        translations = json5.load(open(filePath, encoding="utf-8"))

        self.logger.info("Translation file loaded.")
        return translations

    def translate(self, key: str, *args: str, language: str = "") -> str:
        if language == "":
            language = self.defaultLanguage
        if language not in self.translations:
            self.loadTranslation(language)
        result = self.translations[language].get(key, key)
        if args:
            result = result.format(*map(str, args))
        return result
