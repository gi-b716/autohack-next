from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, cast

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
        default: Any,
        strict: bool = False,
    ) -> None:
        self.types = types
        self.strict = strict
        self._setValue(default)

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


def update_config(version: int) -> Callable:
    def decorator(func: Callable[[dict[str, Any]], None]) -> Callable:
        # Mark the function with its version
        cast(Any, func)._update_version = version  # type: ignore
        return func

    return decorator


class ConfigEntryGroupMeta(type):
    """Metaclass for ConfigEntryGroup that collects update functions."""

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> "ConfigEntryGroupMeta":
        updaters: dict[int, Callable[[dict[str, Any]], None]] = {}

        for key, value in list(namespace.items()):
            func = value
            if isinstance(value, staticmethod):
                func = value.__func__

            if callable(func) and hasattr(func, "_update_version"):
                version = cast(Any, func)._update_version  # type: ignore
                updaters[version] = func  # type: ignore
                del namespace[key]

        cls = super().__new__(mcs, name, bases, namespace)

        cast(Any, cls)._updaters = updaters  # type: ignore

        return cls


class ConfigEntryGroup(metaclass=ConfigEntryGroupMeta):
    _updaters: dict[int, Callable[[dict[str, Any]], None]] = {}

    def __init__(self) -> None:
        pass

    @classmethod
    def iterMembers(cls) -> Iterator[tuple[str, Any]]:
        seen = set()
        for base in reversed(cls.__mro__):
            if base is ConfigEntryGroup or not issubclass(base, ConfigEntryGroup):
                continue
            for key, _value in base.__dict__.items():
                if key.startswith("_") or key in seen:
                    continue
                seen.add(key)
                attr = getattr(cls, key)
                if isinstance(attr, ConfigEntry):
                    yield key, attr
                elif isinstance(attr, type) and issubclass(attr, ConfigEntryGroup):
                    if attr not in (ConfigEntryGroup, cls):
                        yield key, attr

    @classmethod
    def toDict(cls) -> dict[str, Any]:
        result = {}
        for key, attr in cls.iterMembers():
            if isinstance(attr, ConfigEntry):
                result[key] = attr.value
            elif isinstance(attr, type) and issubclass(attr, ConfigEntryGroup):
                result[key] = attr.toDict()
        return result


def _collectUpdaters(group: type[ConfigEntryGroup]) -> dict[int, Callable[[dict[str, Any]], None]]:
    updaters = {}

    if hasattr(group, "_updaters") and group._updaters:
        updaters.update(group._updaters)

    for _key, attr in group.iterMembers():
        if isinstance(attr, type) and issubclass(attr, ConfigEntryGroup):
            updaters.update(_collectUpdaters(attr))

    return updaters


_logger = Logger.getBindLogger("config")


def _loadGroup(group: type[ConfigEntryGroup], data: dict[str, Any], path: list[str]) -> None:
    group_keys = {key for key, _ in group.iterMembers()}
    for k in data.keys():
        if k not in group_keys and k != "version":
            key_path = ".".join(path + [k])
            _logger.warning(f"Unrecognized config entry: {key_path}")

    for key, attr in group.iterMembers():
        if key in data:
            val = data[key]
            if isinstance(attr, ConfigEntry):
                try:
                    attr.value = val
                except TypeError:
                    key_path = ".".join(path + [key])
                    _logger.warning(f"Type mismatch for config entry: {key_path}. Expected {attr.types}, got {type(val).__name__}.")
            elif isinstance(attr, type) and issubclass(attr, ConfigEntryGroup):
                if isinstance(val, dict):
                    _loadGroup(attr, val, path + [key])
                else:
                    key_path = ".".join(path + [key])
                    _logger.warning(f"Type mismatch for config group: {key_path}. Expected dict, got {type(val).__name__}.")


def _upgradeConfig(
    configData: dict[str, Any],
    rootConfig: type[ConfigEntryGroup],
) -> None:
    updaters = _collectUpdaters(rootConfig)

    if not updaters:
        return

    currentVer = configData.get("version", 0)
    maxVer = max(updaters.keys())

    if currentVer < maxVer:
        _logger.info(f"Upgrading config from version {currentVer} to {maxVer}")
        for version in sorted(v for v in updaters.keys() if v > currentVer):
            try:
                updaters[version](configData)
                _logger.debug(f"Applied config update to version {version}")
            except Exception as e:
                _logger.error(f"Error applying config update to version {version}: {e}")

        configData["version"] = maxVer


def loadConfig(configFilePath: Path, rootConfig: type[ConfigEntryGroup]) -> None:
    if not configFilePath.exists():
        _logger.warning(f"Config file {configFilePath} does not exist. Using default config.")

    configData = json5.load(configFilePath.open("r", encoding="utf-8")) if configFilePath.exists() else {}
    oldVersion = configData.get("version", 0)
    _upgradeConfig(configData, rootConfig)
    newVersion = configData.get("version", oldVersion)

    _loadGroup(rootConfig, configData, [])

    if oldVersion != newVersion or not configFilePath.exists():
        saveConfig(configFilePath, rootConfig)


def saveConfig(configFilePath: Path, rootConfig: type[ConfigEntryGroup]) -> None:
    configData = rootConfig.toDict()
    updaters = _collectUpdaters(rootConfig)

    versionedData = {}
    if updaters:
        versionedData["version"] = max(updaters.keys())
    versionedData.update(configData)

    configFilePath.parent.mkdir(parents=True, exist_ok=True)
    configFilePath.write_text(json5.dumps(versionedData, indent=2, quote_keys=True, trailing_commas=False), encoding="utf-8")
