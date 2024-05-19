import json


def json_loads(content, exception:bool=False):
    """
    Convert serialized JSON into dictionary form
    :args:
        content - content to convert into dictionary
        exception:bool - whether to print exception
    :params:
        output - content as dictionary form
    :return:
        output
    """
    output = None
    try:
        return json.loads(content)
    except Exception as error:
        if exception is True:
            print(f"Failed to convert content into dictionary format (Error: {error})")
    return output


def json_dumps(content, indent:int=0, exception:bool=False):
    """
    Convert dictionary into serialized JSON
    :args:
        content - content to convert into dictionary
        indent:int - JSON indent
        exception:bool - whether to print exception
    :params:
        output - content as dictionary form
    :return:
        output
        """
    output = None
    try:
        return json.dumps(content, indent=indent)
    except Exception as error:
        if exception is True:
            print(f"Failed to convert content into serialized JSON format (Error: {error})")
    return output


