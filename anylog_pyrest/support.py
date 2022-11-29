import json
import dotenv


def __read_dotenv(config_file:str, exception:bool=False)->dict:
    """
    Read configs from .env file
    :args:
        config_file:str - .env file to read configs from
        exception:bool - whether or not to write exceptions
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


def print_error(error_type:str, cmd:str, error:str):
    """
    Print Error message
    :args:
        error_type:str - Error Type
        cmd:str - command that failed
        error:str - error message
    :print:
        error message
    """
    if isinstance(error, int): 
        print(f'Failed to execute {error_type} for "{cmd}" (Network Error: {error})')
    else:
        print(f'Failed to execute {error_type} for "{cmd}" (Error: {error})')


def read_configs(config_file:str, exception:bool=False)->dict:
    """
    Given a configuration file, extract configurations
    :supports:
        - .env
        - .yml (to be developed)
    :args:
        config_file:str - YAML file
        exception:bool - whether to write exception
    :params:
        file_extension:str - file extension
        configs:dict - content in YAML file
    :return:
        configs
    """
    file_extension = config_file.rsplit('.', 1)[-1]
    configs = {}

    if file_extension == 'env':
        configs = __read_dotenv(config_file=config_file, exception=exception)
    elif file_extension in ['.yml', '.yaml']:
        pass
    else:
        if exception is True:
            print(f'Invalid extension type: {file_extenson}')

    return configs


def dictionary_merge(yaml_config:dict, anylog_dictionary:dict)->dict:
    """
    Merg dictionary params
    :args:
       yaml_config:dict - YAML configurations
       anylog_dictionary:dict - AnyLog dictionary
    :params:
        full_configs:dict - full list of configurations
    :return:
        full_configs
    """
    full_configs = {}
    for param in yaml_config:
        if param == 'LOCAL_IP':
            full_configs['ip'] = yaml_config[param]
        else:
            full_configs[param.lower()] = yaml_config[param]

    for param in anylog_dictionary:
        if param not in full_configs:
            full_configs[param] = anylog_dictionary[param]

    return full_configs

