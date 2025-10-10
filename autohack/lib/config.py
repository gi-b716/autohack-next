from autohack.core.util import *
from typing import Any
import logging, pathlib, json5, os


class Config:
    def __init__(
        self,
        configFilePath: pathlib.Path,
        defaultConfig: dict[str, Any],
        logger: logging.Logger,
        configValidationExclude: list[str] = [],
        messageOnCreate: str | None = None,
    ) -> None:
        self.defaultConfig = defaultConfig
        self.configValidationExclude = configValidationExclude
        self.configFilePath = configFilePath
        self.logger = logger
        self.logger.info(f'[config] Config file path: "{self.configFilePath}"')
        configFileExists = self.configFileExists()
        self.config = self.loadConfig()
        if not configFileExists and messageOnCreate is not None:
            write(messageOnCreate)
            exitProgram(0)

    def configFileExists(self) -> bool:
        return self.configFilePath.exists()

    def loadConfig(self) -> dict[str, Any]:
        if not os.path.exists(self.configFilePath):
            ensureDirExists(self.configFilePath.parent)
            json5.dump(self.defaultConfig, open(self.configFilePath, "w", encoding="utf-8"), indent=4, quote_keys=True, trailing_commas=False)
            self.logger.info("[config] Config file created.")

        config = json5.load(open(self.configFilePath, "r", encoding="utf-8"))

        # if self.defaultConfig["_version"] > config.get("_version", 0):
        #     mergedConfig = self.mergeConfigs(config, self.defaultConfig)
        #     mergedConfig["_version"] = self.defaultConfig["_version"]
        #     json5.dump(mergedConfig, open(self.configFilePath, "w", encoding="utf-8"), indent=4, quote_keys=True, trailing_commas=False)
        #     write(f"Config file {self.configFilePath} updated to version {self.defaultConfig['_version']}.", 2)
        #     self.logger.info("[config] Config file updated.")
        #     config = mergedConfig

        mergedConfig = self.mergeConfigs(config, self.defaultConfig, self.configValidationExclude, "")
        json5.dump(mergedConfig, open(self.configFilePath, "w", encoding="utf-8"), indent=4, quote_keys=True, trailing_commas=False)
        config = mergedConfig

        self.logger.info("[config] Config file loaded.")
        return config

    def mergeConfigs(self, old: dict[str, Any], newDefault: dict[str, Any], configValidationExclude: list[str], keyName: str) -> dict[str, Any]:
        merged = {}

        for key in newDefault:
            if key in old:
                if isinstance(newDefault[key], dict) and isinstance(old[key], dict):
                    newKeyName = f"{keyName}.{key}" if keyName else key
                    if newKeyName not in configValidationExclude:
                        merged[key] = self.mergeConfigs(old[key], newDefault[key], configValidationExclude, newKeyName)
                    else:
                        merged[key] = old[key]
                else:
                    if type(old[key]) is type(newDefault[key]):
                        merged[key] = old[key]
                    else:
                        merged[key] = newDefault[key]
            else:
                merged[key] = newDefault[key]

        return merged

    def getConfigEntry(self, entryName: str) -> Any:
        entryTree = entryName.split(".")
        result = self.config

        for entryItem in entryTree:
            result = result.get(entryItem, None)
            if result is None:
                break

        self.logger.debug(f'[config] Get config entry: "{entryName}" = "{result}"')
        return result

    def modifyConfigEntry(self, entryName: str, newValue: Any) -> bool:
        """Returns True if the entry was modified, False if it does not exist."""
        entryTree = entryName.split(".")
        currentLevel = self.config

        for level in entryTree[:-1]:
            if not isinstance(currentLevel, dict) or level not in currentLevel:
                return False
            currentLevel = currentLevel[level]
        lastLevel = entryTree[-1]
        if not isinstance(currentLevel, dict) or lastLevel not in currentLevel:
            return False
        currentLevel[lastLevel] = newValue

        json5.dump(self.config, open(self.configFilePath, "w", encoding="utf-8"), indent=4, quote_keys=True, trailing_commas=False)
        self.logger.debug(f'[config] Modify entry: "{entryName}" = "{newValue}"')
        return True
