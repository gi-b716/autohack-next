from typing import Dict, Any
import logging, json, os


class Config:
    DEFAULT_CONFIG: Dict[str, Any] = {
        "version": 3,
        "maximum_number_of_data": 10,
        "time_limit": 1000,
        "memory_limit": 256,
        "error_data_number_limit": 1,
        "filenames": {
            "input": "hack$(id).in",
            "output": "hack$(id).out",
            "answer": "hack$(id).ans",
        },
        "commands": {
            "compile": {
                "source": [
                    "g++",
                    "source.cpp",
                    "-o",
                    "source",
                    "-Wl,--stack=268435456",
                    "-O2",
                ],
                "std": [
                    "g++",
                    "std.cpp",
                    "-o",
                    "std",
                    "-Wl,--stack=268435456",
                    "-O2",
                ],
                "checker": [
                    "g++",
                    "checker.cpp",
                    "-o",
                    "checker",
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
                "checker": [
                    "./checker",
                    "$(outputfile)",
                    "$(ansfile)",
                ],
                "generator": [
                    "./generator",
                ],
            },
        },
        "command_run_at_the_end": "",
    }

    def __init__(self, configFilePath: str, logger: logging.Logger) -> None:
        self.logger = logger
        self.configFilePath = configFilePath
        self.logger.debug(f'[config] Config file path: "{self.configFilePath}"')
        self.config = self.loadConfig()

    def loadConfig(self) -> Dict[str, Any]:
        """
        Load the configuration from the config file.
        """
        if not os.path.exists(self.configFilePath):
            print("Config file not found.\nCreating a new one...", end="")
            json.dump(Config.DEFAULT_CONFIG, open(self.configFilePath, "w"), indent=4)
            print("\rConfig file created.")
            self.logger.info("[config] Config file created.")
            return Config.DEFAULT_CONFIG.copy()

        with open(self.configFilePath, "r") as configFile:
            config = json.load(configFile)

        if Config.DEFAULT_CONFIG["version"] > config.get("version", 0):
            print("Config file version is outdated.\nUpdating...", end="")
            merged_config = self.merge_configs(config, Config.DEFAULT_CONFIG)
            merged_config["version"] = Config.DEFAULT_CONFIG["version"]
            json.dump(merged_config, open(self.configFilePath, "w"), indent=4)
            print("\rConfig file updated.")
            self.logger.info("[config] Config file updated.")
            config = merged_config

        self.logger.info("[config] Config file loaded.")
        return config

    def merge_configs(
        self, old: Dict[str, Any], new_default: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge the old config with the new default config.
        - If a key exists in both, the value from the old config is used.
        - If a key exists only in the new default config, it is added.
        - If a key exists only in the old config, it is ignored.
        """
        merged = {}
        for key in new_default:
            if (
                key in old
                and isinstance(new_default[key], dict)
                and isinstance(old[key], dict)
            ):
                merged[key] = self.merge_configs(old[key], new_default[key])
            else:
                merged[key] = old.get(key, new_default[key])
        return merged

    def getConfigEntry(self, entryName: str) -> Any:
        """
        Get a specific entry from the config file.
        """
        entryTree = entryName.split(".")
        result = self.config

        for entryItem in entryTree:
            result = result.get(entryItem, None)
            if result is None:
                break

        self.logger.debug(f'[config] Get config entry: "{entryName}" = "{result}"')
        return result

    def modifyConfigEntry(self, entryName: str, newValue: Any) -> bool:
        """
        Modify a specific entry in the config file.
        Returns True if the entry was modified, False if it does not exist.
        """
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
