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

