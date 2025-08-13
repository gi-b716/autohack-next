from typing import Dict, Any
import logging, json, sys, os


class Config:
    DEFAULT_CONFIG = {
        "_version": 8,
        "refresh_speed": 10,
        "maximum_number_of_data": 0,
        # ms
        "time_limit": 1000,
        # MiB
        "memory_limit": 256,
        "error_data_number_limit": 1,
        "paths": {
            "input": "$(id)/input",
            "answer": "$(id)/answer",
            "output": "$(id)/output",
        },
        "commands": {
            "compile": {
                "source": [
                    "g++",
                    "source.cpp",
                    "-o",
                    "source",
                    "-O2",
                ],
                "std": [
                    "g++",
                    "std.cpp",
                    "-o",
                    "std",
                    "-O2",
                ],
                "generator": [
                    "g++",
                    "generator.cpp",
                    "-o",
                    "generator",
                    "-O2",
                ],
            },
            "run": {
                "source": [
                    "./source",
                ],
                "std": [
                    "./std",
                ],
                "generator": [
                    "./generator",
                ],
            },
        },
    }

    def __init__(self, configFilePath: str, logger: logging.Logger) -> None:
        self.logger = logger
        self.configFilePath = configFilePath
        self.logger.info(f'[config] Config file path: "{self.configFilePath}"')
        self.config = self.loadConfig()

    def loadConfig(self) -> Dict[str, Any]:
        if not os.path.exists(self.configFilePath):
            json.dump(Config.DEFAULT_CONFIG, open(self.configFilePath, "w"), indent=4)
            self.logger.info("[config] Config file created.")
            print(f"Config file created at {self.configFilePath}.")
            sys.exit(0)
            # return Config.DEFAULT_CONFIG.copy()

        with open(self.configFilePath, "r") as configFile:
            config = json.load(configFile)

        if Config.DEFAULT_CONFIG["_version"] > config.get("_version", 0):
            merged_config = self.mergeConfigs(config, Config.DEFAULT_CONFIG)
            merged_config["_version"] = Config.DEFAULT_CONFIG["_version"]
            json.dump(merged_config, open(self.configFilePath, "w"), indent=4)
            self.logger.info("[config] Config file updated.")
            config = merged_config

        self.logger.info("[config] Config file loaded.")
        return config

    def mergeConfigs(
        self, old: Dict[str, Any], newDefault: Dict[str, Any]
    ) -> Dict[str, Any]:
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

        json.dump(self.config, open(self.configFilePath, "w"), indent=4)
        self.logger.debug(f'[config] Modify entry: "{entryName}" = "{newValue}"')
        return True
