import argparse
import dotenv
import os
import yaml


def __read_dotenv(config_file:str, exception:bool=False)->dict:
    """
    Read configs from .env file
    :args:
        config_file:str - .env file to read configs from
        exception:bool - whether to print exceptions
    :params:
        configs:dict - configs read from .env file
    :return:
        configs
    """
    configs = {}

    try:
        configs = dict(dotenv.dotenv_values(config_file))
    except Exception as error:
        if exception is True:
            print(f'Failed to read configs from {config_file} (Error: {error})')

    return configs


def __read_yaml(config_file:str, exception:bool=False)->dict:
    """
    Read YAML file and store into dictionary - once read flatten to only include relevant configuration
    :args:
        config_file:str - .yml file to read configs from
        exception:bool - whether to print exceptions
    :params:
        configs:dict - configs read from .env file
    :return:
        configs
    """
    configs = {}
    try:
        with open(config_file, 'r') as yaml_file:
            try:
                config_data = yaml.safe_load(yaml_file)
            except Exception as error:
                if exception is True:
                    print(f"Failed to read {config_file} safely (Error: {error})")
    except Exception as error:
        if exception is True:
            print(f"Failed open {config_file} to be read (Error: {error})")
    else:
        for key in config_data:
            if key not in ["metadata", 'image', "other"]:
                configs.update(config_data[key])

    return configs


def check_file(file_path:str, is_argpase:bool=True, exception:bool=False)->str:
    """
    Check whether file exists
    :args:
        file_path:str - file with full path
        is_argpase:bool - (by default) if fails return argparse error
        exception:bool - whether to print exceptions
    :params:
        status:bool
    :return:
        expended full path if success, if fails returns None
    """
    full_path = os.path.expandvars(os.path.expanduser(file_path))
    if not os.path.isfile(full_path):
        full_path = None
        if is_argpase is True:
            raise argparse.ArgumentError(None, f"{file_path}  cannot be found...")
        if exception is True:
            print(f"{file_path}  cannot be found...")

    return full_path


def read_config_file(config_file:str, exception:bool=False)->dict:
    """
    Read configuration file (either .env or .json)
    :args:
        config_file:str - .yml file to read configs from
        exception:bool - whether to print exceptions
    :params:
        full_path:str - validated / expanded full path
        file_extension:str - extension for the file
        configs:dict - configurations from file
    :return:
        configs
    """
    full_path = check_file(file_path=config_file, is_argpase=False, exception=exception)
    file_extension = full_path.rsplit('.', 1)[-1]
    configs = {}

    if full_path is not None:
        if file_extension == 'env':
            configs = __read_dotenv(config_file=full_path, exception=exception)
        elif file_extension in ['yml', 'yaml']:
            configs = __read_yaml(config_file=full_path, exception=exception)
        elif exception is True:
            print(f'Invalid extension type: {file_extension}')

    return configs
