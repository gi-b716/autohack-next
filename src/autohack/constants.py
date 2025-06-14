from platformdirs import user_config_path

CONFIG_NAME = "config.yaml"

CONFIG_LOCATION = user_config_path(appname="autohack", appauthor=False, ensure_exists=True)

CONFIG_FULL_PATH = CONFIG_LOCATION / CONFIG_NAME
