import ast
import json


def json_dumps(content:dict, indent:int=4, exception:bool=False)->str:
    """
    Convert dict to JSON string
    :args:
        content:dict - content to convert
        indent:int - JSON indentation
        exception:bool - whether to print error message if fails to convert
    :return:
        content
    """
    try:
        content = json.dumps(content, indent=indent)
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


def convert_literal(content, exception:bool=False):
    """
    given some value convert to proper format
    :args:
        content - value to convert
        exception:bool - Whether to print error message
    :return:
        converted content
    """
    try:
        content = ast.literal_eval(content)
    except Exception as error:
        if exception is True:
            print(f'Failed to evaluate content (Error: {error})')
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

