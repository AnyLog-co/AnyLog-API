import ast
import json


def __format_merged_dict(configs:dict)->dict:
    """
    iterate through configs and update values to correct type
    :args:
        configs:dict - dictionary to iterate through
    else:
        updated configs
    """
    for key in configs:
        if configs[key].lower() == 'true':
            configs[key] = True
        elif configs[key].lower() == 'false':
            configs[key] = False
        else:
            try:
                configs[key] = int(configs[key])
            except:
                pass
    return configs


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


def dictionary_merge(file_config:dict, anylog_config:dict, exception:bool=False)->dict:
    """
    Merg dictionary params
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

    for param in anylog_config:
        if param not in full_configs:
            full_configs[param] = anylog_config[param]

    return __format_merged_dict(configs=full_configs)


