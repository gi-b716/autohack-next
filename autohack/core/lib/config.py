from pathlib import Path
from typing import Any, Iterator

import json5

from autohack.core.lib.logger import Logger


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
        rootConfig: type[ConfigEntryGroup],
    ) -> None:
        self.configFilePath = configFilePath
        self.rootConfig = rootConfig
        self._logger = Logger.getBindLogger("config")

        self._load()

    def _loadGroup(self, group: type[ConfigEntryGroup], data: dict[str, Any], path: list[str]) -> None:
        group_keys = {key for key, _ in group.iterMembers()}
        for k in data.keys():
            if k not in group_keys:
                key_path = ".".join(path + [k])
                self._logger.warning(f"Unrecognized config entry: {key_path}")

        for key, attr in group.iterMembers():
            if key in data:
                val = data[key]
                if isinstance(attr, ConfigEntry):
                    try:
                        attr.value = val
                    except TypeError:
                        key_path = ".".join(path + [key])
                        self._logger.warning(f"Type mismatch for config entry: {key_path}. Expected {attr.types}, got {type(val).__name__}.")
                elif isinstance(attr, type) and issubclass(attr, ConfigEntryGroup):
                    if isinstance(val, dict):
                        self._loadGroup(attr, val, path + [key])
                    else:
                        key_path = ".".join(path + [key])
                        self._logger.warning(f"Type mismatch for config group: {key_path}. Expected dict, got {type(val).__name__}.")

    def _load(self) -> None:
        if not self.configFilePath.exists():
            self._logger.warning(f"Config file {self.configFilePath} does not exist. Using default config.")

        configFile = json5.load(self.configFilePath.open("r", encoding="utf-8")) if self.configFilePath.exists() else {}
        self._loadGroup(self.rootConfig, configFile, [])


def loadConfig(configFilePath: Path, rootConfig: type[ConfigEntryGroup]):
    Config(configFilePath, rootConfig)
