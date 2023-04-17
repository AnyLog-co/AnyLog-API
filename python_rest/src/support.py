import ast
import json


def json_dumps(content:dict, indent:int=4, exception:bool=False):
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
            print(f'Failed to convert content into JSON string (Error: {error})')

    return content


def json_loads(content:str, exception:bool=False):
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
    if content.lower() == 'true':
        content = True
    elif content.lower() ==  'false':
        content = False
    else:
        try:
            content = ast.literal_eval(content)
        except Exception as error:
            if exception is True:
                print(f'{content} - Failed to evaluate content (Error: {error})')

    return content


def dictionary_merge(file_config:dict, anylog_config:dict):
    """
    Merge dictionary params
    :args:
       file_config:dict - file configurations
       anylog_config:dict - AnyLog dictionary
    :params:
        full_configs:dict - full list of configurations
    :return:
        full_configs
    """
    full_configs = {}
    for param in file_config:
        if param == 'LOCAL_IP':
            full_configs['ip'] = file_config[param]
        else:
            full_configs[param.lower()] = file_config[param]

    print(anylog_config)
    print(file_config)
    for param in anylog_config:
        if param not in full_configs:
            full_configs[param] = anylog_config[param]

    for key in full_configs:
        if full_configs[key].lower() == 'true':
            full_configs[key] = True
        elif full_configs[key].lower() == 'false':
            full_configs[key] = False
        else:
            try:
                full_configs[key] = int(full_configs[key])
            except:
                pass

    return full_configs
