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
