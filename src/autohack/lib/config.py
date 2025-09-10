from autohack.core.util import *
from typing import Any
import logging, pathlib, json, os


class Config:
    def __init__(
        self,
        configFilePath: pathlib.Path,
        defaultConfig: dict[str, Any],
        logger: logging.Logger,
    ) -> None:
        self.defaultConfig = defaultConfig
        self.configFilePath = configFilePath
        self.logger = logger
        self.logger.info(f'[config] Config file path: "{self.configFilePath}"')
        self.config = self.loadConfig()

    def loadConfig(self) -> dict[str, Any]:
        if not os.path.exists(self.configFilePath):
            json.dump(
                self.defaultConfig,
                open(self.configFilePath, "w", encoding="utf-8"),
                indent=4,
            )
            self.logger.info("[config] Config file created.")
            write(f"Config file created at {self.configFilePath}.")
            exitProgram(0)

        with open(self.configFilePath, "r", encoding="utf-8") as configFile:
            config = json.load(configFile)

        if self.defaultConfig["_version"] > config.get("_version", 0):
            mergedConfig = self.mergeConfigs(config, self.defaultConfig)
            mergedConfig["_version"] = self.defaultConfig["_version"]
            json.dump(
                mergedConfig, open(self.configFilePath, "w", encoding="utf-8"), indent=4
            )
            write(
                f"Config file {self.configFilePath} updated to version {self.defaultConfig['_version']}.",
                2,
            )
            self.logger.info("[config] Config file updated.")
            config = mergedConfig

        self.logger.info("[config] Config file loaded.")
        return config

    def mergeConfigs(
        self, old: dict[str, Any], newDefault: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Merge the old config with the new default config.
        - If a key exists in both, the value from the old config is used.
        - If a key exists only in the new default config, it is added.
        - If a key exists only in the old config, it is ignored.
        """
        merged = {}
        for key in newDefault:
            if (
                key in old
                and isinstance(newDefault[key], dict)
                and isinstance(old[key], dict)
            ):
                merged[key] = self.mergeConfigs(old[key], newDefault[key])
            else:
                merged[key] = old.get(key, newDefault[key])
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

        json.dump(
            self.config, open(self.configFilePath, "w", encoding="utf-8"), indent=4
        )
        self.logger.debug(f'[config] Modify entry: "{entryName}" = "{newValue}"')
        return True
