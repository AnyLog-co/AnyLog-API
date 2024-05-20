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


def add_conditions(headers:dict, **conditions):
    """
    Adds conditions to the 'command' key in the headers dictionary.
    :args:
        headers (dict): The headers dictionary containing the 'command' key.
        **conditions: Arbitrary keyword arguments representing conditions to be added.
    :returns:
        None: The function modifies the headers dictionary in place.
    """
    condition_list = []
    for key, value in conditions:
        if isinstance(value, bool) and value is True:
            condition_list.append(f"{key}=true")
        elif isinstance(value, bool) and value is False:
            condition_list.append(f"{key}=false")
        elif value is not None:
            condition_list.append(f"{key}={value}")
            
    if condition_list:
        headers['command'] += " where " + " and ".join(condition_list)

