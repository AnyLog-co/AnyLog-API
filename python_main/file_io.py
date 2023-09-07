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


def check_file(config_file:str, is_argparse:bool=True, exception:bool=False):
    """
    Check if file exists
    :args:
        config_file:str - configuration file
        is_argparse:bool - whether code is in argument-parse mode or not
        exception:bool - whether to print exception if not in argument-parse mode
    :params:
        full_path:str - full path of file
    :return:
        full_path
    """
    full_path = os.path.expanduser(os.path.expandvars(config_file))
    if not os.path.isfile(full_path):
        full_path = None
        if is_argparse is True:
            raise argparse.ArgumentError(None, f"Failed to locate configuration file {config_file}")
        if exception is True:
            print(f"Failed to locate configuration file {config_file}")

    return full_path


def read_configs(config_file:str, exception:bool=False):
    """
    Read configuration file
    :args:
        config_file:str - configuration file
        exception:bool - whether to print exceptions
    :params:
        file_configs:dict - configurations form file
        full_path:str - full file path
        file_ext:str - file extension
    :return:
        file_configs
    """
    file_configs = {}
    full_path = check_file(config_file=config_file, is_argparse=False, exception=exception)
    if full_path is None:
        return file_configs

    file_ext = full_path.rsplit('.', 1)[-1]
    if file_ext == 'env':
        file_configs = __read_dotenv(config_file=full_path, exception=exception)
    elif file_ext in ['yml', 'yaml']:
        file_configs = __read_yaml(config_file=full_path, exception=exception)
    else:
        print(f'Invalid extension type: {file_ext}')

    return file_configs


