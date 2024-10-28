import argparse
import dotenv
import os.path

def check_configs(config_files:str):
    """
    Check configuration file(s)
    :args:
        config_files:str - user input configs
    :params:
        configs:list - config_files as a list
        error_msg:str - error message (used for raise)
        :raise:
        if err_msg != ""
    :return:
        config_files
    """
    configs = []
    error_msg = ""
    for config in config_files.split(","):
        full_path = os.path.expanduser(os.path.expandvars(config))
        if not os.path.isfile(full_path):
            error_msg += f"Missing config file {full_path}\n"
        else:
            configs.append(full_path)
    if error_msg != "":
        raise argparse.ArgumentTypeError(error_msg)

    return configs


def read_configs(config_file:str, exception:bool=False)->dict:
    """
    Read configuration files
    :args:
        config_file:str - configuration file to read
        exception: whether to print exceptions
    :params:
        configs:dict - output from file
    :return:
        configs
    """
    configs = {}
    if isinstance(config_file, list):
        for config in config_file:
            output =   read_configs(config_file=config, exception=exception)
            configs = {**configs, **output}
    else:
        try:
           configs = dotenv.dotenv_values(config_file)
        except Exception as error:
            if exception is True:
                print(f"Failed to read config file {config_file} (Error: {error})")
    if len(configs) > 0: # convert to lower case keys
        return {key.lower(): value for key, value in configs.items()}
    return configs

