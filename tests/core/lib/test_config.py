import pytest


def test_typeCheck():
    from autohack.core.lib.config import _typeCheck

    assert _typeCheck(10, int, False)
    assert _typeCheck(10, (int, str), False)
    assert not _typeCheck(10, str, False)
    assert _typeCheck(10, int, True)
    assert _typeCheck(10, (int, str), True)
    assert not _typeCheck(10, str, True)

    assert _typeCheck(True, int, False)
    assert not _typeCheck(True, int, True)


def test_ConfigEntry():
    from autohack.core.lib.config import ConfigEntry

    entry = ConfigEntry(int, 10)

    assert entry.value == 10

    with pytest.raises(TypeError):
        entry.value = "not an int"

    entry.value = 20
    assert entry.value == 20

    with pytest.raises(TypeError):
        entry = ConfigEntry(str, 10)

    entry = ConfigEntry((int, str), 10)
    assert entry.value == 10
    entry.value = "now a string"
    assert entry.value == "now a string"
    with pytest.raises(TypeError):
        entry.value = [1, 2, 3]

    with pytest.raises(TypeError):
        entry = ConfigEntry(int, False, strict=True)


def test_ConfigEntryGroup():
    from autohack.core.lib.config import ConfigEntry, ConfigEntryGroup

    class CustomSubGroup(ConfigEntryGroup):
        SUB_ENTRY_1 = ConfigEntry(bool, True)
        SUB_ENTRY_2 = ConfigEntry(float, 3.14)

    class CustomGroup(ConfigEntryGroup):
        CONFIG_ENTRY_1 = ConfigEntry(int, 10)
        CONFIG_ENTRY_2 = ConfigEntry(str, "default")
        SUB_GROUP = CustomSubGroup

    assert CustomGroup.toDict() == {
        "CONFIG_ENTRY_1": 10,
        "CONFIG_ENTRY_2": "default",
        "SUB_GROUP": {"SUB_ENTRY_1": True, "SUB_ENTRY_2": 3.14},
    }

    for key, value in CustomGroup.iterMembers():
        if key == "CONFIG_ENTRY_1":
            assert isinstance(value, ConfigEntry)
            assert value.value == 10
        elif key == "CONFIG_ENTRY_2":
            assert isinstance(value, ConfigEntry)
            assert value.value == "default"
        elif key == "SUB_GROUP":
            assert type(value) is type(CustomSubGroup)
            assert value.SUB_ENTRY_1.value is True
            assert value.SUB_ENTRY_2.value == 3.14


def test_Config(tmp_path):
    import json5

    from autohack.core.lib.config import ConfigEntry, ConfigEntryGroup, loadConfig

    class SubGroup(ConfigEntryGroup):
        SUB_1 = ConfigEntry(int, 1)

    class RootGroup(ConfigEntryGroup):
        ENTRY_1 = ConfigEntry(str, "test")
        SUB = SubGroup

    config_path = tmp_path / "config.json"

    loadConfig(config_path, RootGroup)
    assert RootGroup.ENTRY_1.value == "test"
    assert RootGroup.SUB.SUB_1.value == 1

    with open(config_path, "w", encoding="utf-8") as f:
        json5.dump({"ENTRY_1": "updated", "SUB": {"SUB_1": 2}}, f)

    loadConfig(config_path, RootGroup)
    assert RootGroup.ENTRY_1.value == "updated"
    assert RootGroup.SUB.SUB_1.value == 2

    RootGroup.ENTRY_1.value = "test"
    RootGroup.SUB.SUB_1.value = 1

    with open(config_path, "w", encoding="utf-8") as f:
        json5.dump({"ENTRY_1": 123, "EXTRA": "extra_val", "SUB": {"SUB_1": "not int", "EXTRA_SUB": 2}}, f)

    loadConfig(config_path, RootGroup)
    assert RootGroup.ENTRY_1.value == "test"
    assert RootGroup.SUB.SUB_1.value == 1


def test_config_version_upgrade(tmp_path):
    from typing import Any

    import json5

    from autohack.core.lib.config import (
        ConfigEntry,
        ConfigEntryGroup,
        loadConfig,
        update_config,
    )

    class RootGroup(ConfigEntryGroup):
        NAME = ConfigEntry(str, "default_name")
        VALUE = ConfigEntry(int, 10)
        NEW_FIELD = ConfigEntry(str, "new_default")

        @staticmethod
        @update_config(version=35)
        def _update_to_35(config: dict[str, Any]) -> None:
            config.setdefault("NEW_FIELD", "new_default")

        @staticmethod
        @update_config(version=36)
        def _update_to_36(config: dict[str, Any]) -> None:
            if "VALUE" in config:
                config["VALUE"] = config["VALUE"] * 2

    config_path = tmp_path / "config.json"

    with open(config_path, "w", encoding="utf-8") as f:
        json5.dump({"@version": 34, "NAME": "test", "VALUE": 5}, f)

    loadConfig(config_path, RootGroup)
    assert RootGroup.NAME.value == "test"
    assert RootGroup.VALUE.value == 10
    assert RootGroup.NEW_FIELD.value == "new_default"

    with open(config_path, encoding="utf-8") as f:
        saved_data = json5.load(f)
    assert saved_data["@version"] == 36

    RootGroup.NAME.value = "default_name"
    RootGroup.VALUE.value = 10
    RootGroup.NEW_FIELD.value = "new_default"

    with open(config_path, "w", encoding="utf-8") as f:
        json5.dump({"NAME": "test2", "VALUE": 3}, f)

    loadConfig(config_path, RootGroup)
    assert RootGroup.NAME.value == "test2"
    assert RootGroup.VALUE.value == 6
    assert RootGroup.NEW_FIELD.value == "new_default"

    RootGroup.NAME.value = "default_name"
    RootGroup.VALUE.value = 10
    RootGroup.NEW_FIELD.value = "new_default"

    with open(config_path, "w", encoding="utf-8") as f:
        json5.dump({"@version": 36, "NAME": "test3", "VALUE": 5, "NEW_FIELD": "custom"}, f)

    loadConfig(config_path, RootGroup)
    assert RootGroup.NAME.value == "test3"
    assert RootGroup.VALUE.value == 5
    assert RootGroup.NEW_FIELD.value == "custom"


def test_save_config_value(tmp_path):
    from typing import Any

    import json5

    from autohack.core.lib.config import ConfigEntry, ConfigEntryGroup, loadConfig, saveConfig, update_config

    class SubGroup(ConfigEntryGroup):
        SUB_VALUE = ConfigEntry(int, 100)

    class RootGroup(ConfigEntryGroup):
        NAME = ConfigEntry(str, "default")
        SUB = SubGroup

        @staticmethod
        @update_config(version=1)
        def _update_to_1(config: dict[str, Any]) -> None:
            pass

    config_path = tmp_path / "config.json"

    loadConfig(config_path, RootGroup)

    RootGroup.NAME.value = "updated_name"
    assert RootGroup.NAME.value == "updated_name"
    saveConfig(config_path, RootGroup)

    with open(config_path, encoding="utf-8") as f:
        saved_data = json5.load(f)
    assert saved_data["NAME"] == "updated_name"

    RootGroup.SUB.SUB_VALUE.value = 200
    assert RootGroup.SUB.SUB_VALUE.value == 200
    saveConfig(config_path, RootGroup)

    with open(config_path, encoding="utf-8") as f:
        saved_data = json5.load(f)
    assert saved_data["SUB"]["SUB_VALUE"] == 200


def test_load_and_save_functions(tmp_path):
    from typing import Any

    import json5

    from autohack.core.lib.config import ConfigEntry, ConfigEntryGroup, loadConfig, saveConfig, update_config

    class RootGroup(ConfigEntryGroup):
        NAME = ConfigEntry(str, "default")
        VALUE = ConfigEntry(int, 42)

        @staticmethod
        @update_config(version=1)
        def _update_to_1(config: dict[str, Any]) -> None:
            pass

    config_path = tmp_path / "config.json"

    loadConfig(config_path, RootGroup)
    assert RootGroup.NAME.value == "default"
    assert RootGroup.VALUE.value == 42

    RootGroup.NAME.value = "updated"
    assert RootGroup.NAME.value == "updated"
    saveConfig(config_path, RootGroup)

    with open(config_path, encoding="utf-8") as f:
        data = json5.load(f)
    assert data["NAME"] == "updated"
    assert data["@version"] == 1
