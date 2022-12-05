import json
import dotenv
import os


def json_dumps(content:dict, exception:bool=False)->str:
    """
    Convert dict to JSON string
    :args:
        content:dict - content to convert
        exception:bool - whether or not to print error message if fails to convert
    :return:
        content
    """
    try:
        content = json.dumps(content)
    except Exception as error:
        if exception is True:
            print(f'Failed to convert content into JSON string')
    return content


def json_loads(content:str, exception:bool=False)->dict:
    """
    Convert JSON-string to dict
    :args:
        content:dict - content to convert
        exception:bool - whether or not to print error message if fails to convert
    :return:
        content
    """
    try:
        content = json.load(content)
    except Exception as error:
        if exception is True:
            print(f'Failed to convert content into JSON string')
    return content


def generic_write(file_path:str, content:str, exception:bool=False)->bool:
    status = True
    if not os.path.isfile(file_path):
        try:
            open(file_path, 'w').close()
        except Exception as error:
            status = False
            if exception is True:
                print(f'Failed to create file: {file_path} (Error: {error})')

    if status is True:
        try:
            with open(file_path, 'a') as f:
                try:
                    f.write(content)
                except Exception as error:
                    status = False
                    if exception is True:
                        print(f'Failed to write content in file {file_path} (Error: {error})')
        except Exception as error:
            status = False
            if exception is True:
                print(f'Failed to open file {file_path} to append content (Error: {error})')

    return status


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


def print_rest_error(error_type:str, cmd:str, error:str):
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

