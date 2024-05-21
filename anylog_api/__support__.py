import json
import re


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
    Adds conditions to the 'command' key in the header dictionary
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


def check_interval(time_interval:str, exception:bool=False)->bool:
    """
    Validate if user-defined interval is supported
    :args:
        time_interval:str - user defined interval
        exception:bool - whether to print exception
    :params:
        status:bool
        time_interval_pattern:str - supported intervals
    :return:
        True - valid interval
        False - invalid interval
    """
    status = True
    time_interval_pattern = r'^\d*\s*(second|seconds|minute|minutes|day|days|month|months|year|years)$'

    if not bool(re.match(time_interval_pattern, time_interval.strip())):
        if exception is True:
            print(f"Interval value {time_interval} - time interval options: second, minute, day, month or year")
        status = False

    return status