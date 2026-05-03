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

    assert CustomGroup.todict() == {
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
    import json

    from autohack.core.lib.config import Config, ConfigEntry, ConfigEntryGroup

    class SubGroup(ConfigEntryGroup):
        SUB_1 = ConfigEntry(int, 1)

    class RootGroup(ConfigEntryGroup):
        ENTRY_1 = ConfigEntry(str, "test")
        SUB = SubGroup

    config_path = tmp_path / "config.json"

    # Test 1: File doesn't exist (uses defaults)
    config = Config(config_path, RootGroup)
    config._load()
    assert RootGroup.ENTRY_1.value == "test"
    assert RootGroup.SUB.SUB_1.value == 1

    # Test 2: Normal load
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({"ENTRY_1": "updated", "SUB": {"SUB_1": 2}}, f)

    config = Config(config_path, RootGroup)
    config._load()
    assert RootGroup.ENTRY_1.value == "updated"
    assert RootGroup.SUB.SUB_1.value == 2

    # Test 3: Type mismatch & extra keys
    RootGroup.ENTRY_1.value = "test"
    RootGroup.SUB.SUB_1.value = 1

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "ENTRY_1": 123,
                "EXTRA": "extra_val",
                "SUB": {"SUB_1": "not int", "EXTRA_SUB": 2},
            },
            f,
        )

    config = Config(config_path, RootGroup)
    config._load()
    # Should stay at defaults due to type error
    assert RootGroup.ENTRY_1.value == "test"
    assert RootGroup.SUB.SUB_1.value == 1
