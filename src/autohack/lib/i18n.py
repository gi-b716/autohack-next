from typing import Dict
import logging, json, os


class I18N:
    def __init__(
        self,
        translationFileDir: str,
        language: str,
        logger: logging.Logger,
    ) -> None:
        self.translationFile = os.path.join(translationFileDir, language)
        self.logger = logger
        self.logger.info(f"[i18n] Translation file: {self.translationFile}")
        self.translations = self.loadTranslationFile()

    def loadTranslationFile(self) -> Dict[str, str]:
        if not os.path.exists(self.translationFile):
            self.logger.critical("[i18n] Translation file not found.")
            raise FileNotFoundError(
                f"Translation file {self.translationFile} not found."
            )
        with open(self.translationFile, "r", encoding="utf-8") as translationFile:
            translations = json.load(translationFile)

        self.logger.info("[i18n] Translation file loaded.")
        return translations

    def translate(self, key: str) -> str:
        return self.translations.get(key, key)
