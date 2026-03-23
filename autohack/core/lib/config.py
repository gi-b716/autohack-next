from pathlib import Path
from typing import Any, Iterator
import os

import json5

from autohack.core.util import *


def _typeCheck(value: Any, types: type | tuple[type, ...], strict: bool) -> bool:
    if strict:
        return type(value) in (types if isinstance(types, tuple) else (types,))
    else:
        return isinstance(value, types)


class ConfigEntry:
    def __init__(
        self,
        types: type | tuple[type, ...],
        defaultValue: Any,
        strict: bool = False,
    ) -> None:
        """
        if not isinstance(types, tuple):
            types = (types,)

        if strict:
            if type(defaultValue) not in types:
                raise TypeError(f"Type of defaultValue must be exactly one of {types}")
        else:
            if not isinstance(defaultValue, types):
                raise TypeError(f"Type of defaultValue must be in {types}")
        """

        self.types = types
        self.strict = strict
        self._setValue(defaultValue)

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new: Any) -> None:
        self._setValue(new)

    def _setValue(self, new: Any) -> None:
        if not _typeCheck(new, self.types, self.strict):
            raise TypeError(f"Type of new value must be {'exactly one of' if self.strict else 'in'} {self.types}")
        self._value = new


class ConfigEntryGroup:
    def __init__(self) -> None:
        pass

    @classmethod
    def iterMembers(cls) -> Iterator[tuple[str, Any]]:
        for key in dir(cls):
            if key.startswith("_"):
                continue
            attr = getattr(cls, key)
            if isinstance(attr, ConfigEntry):
                yield key, attr
            elif isinstance(attr, type) and issubclass(attr, ConfigEntryGroup):
                if attr not in (ConfigEntryGroup, cls):
                    yield key, attr

    @classmethod
    def todict(cls) -> dict[str, Any]:
        result = {}
        for key, attr in cls.iterMembers():
            if isinstance(attr, ConfigEntry):
                result[key] = attr.value
            elif isinstance(attr, type) and issubclass(attr, ConfigEntryGroup):
                result[key] = attr.todict()
        return result


class Config:
    def __init__(
        self,
        configFilePath: Path,
        defaultConfig: dict[str, Any],
        logger: Any,
        configValidationExclude: list[str] = [],
        messageOnCreate: str | None = None,
    ) -> None:
        self.defaultConfig = defaultConfig
        self.configValidationExclude = configValidationExclude
        self.configFilePath = configFilePath
        self.logger = logger.bind(module="config")
        self.logger.info(f'Config file path: "{self.configFilePath}"')
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
            self.logger.info("Config file created.")

        config = json5.load(open(self.configFilePath, "r", encoding="utf-8"))

        # if self.defaultConfig["_version"] > config.get("_version", 0):
        #     mergedConfig = self.mergeConfigs(config, self.defaultConfig)
        #     mergedConfig["_version"] = self.defaultConfig["_version"]
        #     json5.dump(mergedConfig, open(self.configFilePath, "w", encoding="utf-8"), indent=4, quote_keys=True, trailing_commas=False)
        #     write(f"Config file {self.configFilePath} updated to version {self.defaultConfig['_version']}.", 2)
        #     self.logger.info("Config file updated.")
        #     config = mergedConfig

        mergedConfig = self.mergeConfigs(config, self.defaultConfig, self.configValidationExclude, "")
        json5.dump(mergedConfig, open(self.configFilePath, "w", encoding="utf-8"), indent=4, quote_keys=True, trailing_commas=False)
        config = mergedConfig

        self.logger.info("Config file loaded.")
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

        self.logger.debug(f'Get config entry: "{entryName}" = "{result}"')
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
        self.logger.debug(f'Modify entry: "{entryName}" = "{newValue}"')
        return True
