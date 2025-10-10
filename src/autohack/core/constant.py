from typing import Any

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


# Do not modify checker args here, as they may contain user data.
# They are excluded from config validation for the same reason.
CONFIG_VALIDATION_EXCLUDE = ["checker.args"]

DEFAULT_GLOBAL_CONFIG = {
    "language": "en_US",
    "refresh_speed": 10,
    "wait_time_before_start": 3,
    "data_folder_max_size": 256,  # MB
}

# empty: For developers to test missing translations.
LANGUAGE_MAPS = ["en_US", "zh_CN", "empty"]

LOGGER_LANGUAGE_ID = "en_US"
