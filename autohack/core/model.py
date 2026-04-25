from autohack.core.lib.config import ConfigEntry, ConfigEntryGroup


class GlobalConfigRoot(ConfigEntryGroup):
    language = ConfigEntry(str, "en_US")
    refresh_speed = ConfigEntry(int, 10)
    wait_time_before_start = ConfigEntry(int, 3)
    data_folder_max_size = ConfigEntry(int, 256)


class ConfigPaths(ConfigEntryGroup):
    input = ConfigEntry(str, "$(id)/input")
    answer = ConfigEntry(str, "$(id)/answer")
    output = ConfigEntry(str, "$(id)/output")


class ConfigCommandsCompile(ConfigEntryGroup):
    source = ConfigEntry(list, ["g++", "source.cpp", "-o", "source", "-O2"])
    std = ConfigEntry(list, ["g++", "std.cpp", "-o", "std", "-O2"])
    generator = ConfigEntry(list, ["g++", "generator.cpp", "-o", "generator", "-O2"])


class ConfigCommandsRun(ConfigEntryGroup):
    source = ConfigEntry(list, ["./source"])
    std = ConfigEntry(list, ["./std"])
    generator = ConfigEntry(list, ["./generator"])


class ConfigCommands(ConfigEntryGroup):
    compile = ConfigCommandsCompile
    run = ConfigCommandsRun


class ConfigChecker(ConfigEntryGroup):
    name = ConfigEntry(str, "builtin_basic")
    args = ConfigEntry(dict, {})


class ConfigRoot(ConfigEntryGroup):
    maximum_number_of_data = ConfigEntry(int, 0)
    time_limit = ConfigEntry(int, 1000)
    memory_limit = ConfigEntry(int, 256)
    error_data_number_limit = ConfigEntry(int, 1)
    paths = ConfigPaths
    commands = ConfigCommands
    checker = ConfigChecker
    command_at_end = ConfigEntry(str, "")
