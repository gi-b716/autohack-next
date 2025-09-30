from typing import Any

VERSION = "1.0.12"

# Windows executables will use this version.
VERSION_ID = "1.0.12"

WAIT_TIME_BEFORE_START = 3

DATA_FOLDER_MAX_SIZE = 256  # 256 MiB

DEFAULT_CONFIG: dict[str, Any] = {
    "_version": 11,
    "refresh_speed": 10,
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
    "_version": 1,
    "language": "en_US",
}

# empty: For developers to test missing translations.
LANGUAGE_MAPS = ["en_US", "zh_CN", "empty"]

LOGGER_LANGUAGE_ID = "en_US"
