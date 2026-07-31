from typing import Any

CONFIG_VERSION_FIELD = "@version"

DEFAULT_CONFIG: dict[str, Any] = {
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
    "checker": {
        "name": "builtin_basic",
        "args": {},
    },
    "command_at_end": "",
}


DEFAULT_GLOBAL_CONFIG = {
    "language": "en_US",
    "refresh_speed": 10,
    "wait_time_before_start": 3,
    "data_folder_max_size": 256,  # MB
    "override": {},
}

# Supported language IDs (also used as Crowdin locale codes).
LANGUAGE_MAPS = ["en-US", "zh-CN"]

DEFAULT_LANGUAGE_ID = "en-US"

SYSTEM_LOCALE_TO_LANG: dict[str, str] = {
    "zh_CN": "zh-CN",
    "zh_SG": "zh-CN",
    "zh": "zh-CN",
    "en_US": "en-US",
    "en_GB": "en-US",
    "en": "en-US",
}

AUTO_DETECT_LANG_SENTINEL = "__auto_detect__"
