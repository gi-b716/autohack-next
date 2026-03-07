from typing import Any
from autohack.core.constant import *
import logging, pathlib, json5, os


class I18N:
    def __init__(
        self,
        translationFileDir: pathlib.Path,
        logger: Any,
    ) -> None:
        self.translationFileDir = translationFileDir
        self.logger = logger.bind(module="i18n")
        self.translations = {}
        self.setDefaultLanguage(LOGGER_LANGUAGE_ID)

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
        translations = json5.load(open(filePath, "r", encoding="utf-8"))

        self.logger.info("Translation file loaded.")
        return translations

    def translate(self, key: str, language: str = "") -> str:
        if language == "":
            language = self.defaultLanguage
        if language not in self.translations:
            self.loadTranslation(language)
        return self.translations[language].get(key, key)
