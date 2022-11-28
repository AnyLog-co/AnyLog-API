import json
import yaml

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
    Given a configuration file (YAML format) convert to be useable
    :args:
        config_filee:str - YAML file
        exception:bool - whether to write exception
    :params:
        content:dict - content in YAML file
    :return:
        content
    """
    content = {}
    try:
        with open(config_file, 'r') as f:
            try:
                content = yaml.safe_load(f)
            except Exception as e:
                if exception is True:
                    print(f'Failed to read content in {config_file} (Error: {e}')
    except Exception as e:
        print(f'Failed to open {config_file} (Error: {e})')
    return content


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

