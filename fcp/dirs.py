from appdirs import *


def get_config_dir():
    appname = "fcp"
    appauthor = "joaj"
    config = user_data_dir(appname, appauthor)
    os.makedirs(config, exist_ok=True)

    return config
