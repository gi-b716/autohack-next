from typing import Any

from autohack.core.constant import DEFAULT_CONFIG, DEFAULT_GLOBAL_CONFIG
from autohack.core.lib.config import ConfigEntry, ConfigEntryGroup, update_config
from autohack.core.util.ansi import ANSIHelper
from autohack.core.util.console import write


class GlobalConfigRoot(ConfigEntryGroup):
    language = ConfigEntry(str, DEFAULT_GLOBAL_CONFIG["language"])
    refresh_speed = ConfigEntry(int, DEFAULT_GLOBAL_CONFIG["refresh_speed"])
    wait_time_before_start = ConfigEntry(int, DEFAULT_GLOBAL_CONFIG["wait_time_before_start"])
    data_folder_max_size = ConfigEntry(int, DEFAULT_GLOBAL_CONFIG["data_folder_max_size"])
    # override = ConfigEntry(dict, DEFAULT_GLOBAL_CONFIG["override"])

    @staticmethod
    @update_config(version=1)
    def _update_to_1(config: dict[str, Any]) -> None:
        write(ANSIHelper.colorText("Config structure has been upgraded. / 配置结构已升级。", [ANSIHelper.MAGENTA, ANSIHelper.BOLD]), endl=1)


class ConfigPaths(ConfigEntryGroup):
    input = ConfigEntry(str, DEFAULT_CONFIG["paths"]["input"])
    answer = ConfigEntry(str, DEFAULT_CONFIG["paths"]["answer"])
    output = ConfigEntry(str, DEFAULT_CONFIG["paths"]["output"])


class ConfigCommandsCompile(ConfigEntryGroup):
    source = ConfigEntry(list, DEFAULT_CONFIG["commands"]["compile"]["source"])
    std = ConfigEntry(list, DEFAULT_CONFIG["commands"]["compile"]["std"])
    generator = ConfigEntry(list, DEFAULT_CONFIG["commands"]["compile"]["generator"])


class ConfigCommandsRun(ConfigEntryGroup):
    source = ConfigEntry(list, DEFAULT_CONFIG["commands"]["run"]["source"])
    std = ConfigEntry(list, DEFAULT_CONFIG["commands"]["run"]["std"])
    generator = ConfigEntry(list, DEFAULT_CONFIG["commands"]["run"]["generator"])


class ConfigCommands(ConfigEntryGroup):
    compile = ConfigCommandsCompile
    run = ConfigCommandsRun


class ConfigChecker(ConfigEntryGroup):
    name = ConfigEntry(str, DEFAULT_CONFIG["checker"]["name"])
    args = ConfigEntry(dict, DEFAULT_CONFIG["checker"]["args"])


class ConfigRoot(ConfigEntryGroup):
    maximum_number_of_data = ConfigEntry(int, DEFAULT_CONFIG["maximum_number_of_data"])
    time_limit = ConfigEntry(int, DEFAULT_CONFIG["time_limit"])
    memory_limit = ConfigEntry(int, DEFAULT_CONFIG["memory_limit"])
    error_data_number_limit = ConfigEntry(int, DEFAULT_CONFIG["error_data_number_limit"])
    paths = ConfigPaths
    commands = ConfigCommands
    checker = ConfigChecker
    command_at_end = ConfigEntry(str, DEFAULT_CONFIG["command_at_end"])
