"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import json
import re


def json_loads(content, exception:bool=False)->dict:
    """
    Convert serialized JSON into dictionary form
    :args:
        content - content to convert into dictionary
        exception:bool - whether to print exception
    :params:
        output - content as dictionary form
    :return:
        output
        if fails - raise JSON error
    """
    output = None
    try:
        output = json.loads(content)
    except Exception as error:
        if exception is True:
            raise json.JSONDecodeError(msg=f"Failed to convert content into dictionary format (Error: {error})",
                                       doc=content, pos=0)

    return output


def json_dumps(content, indent:int=0, exception:bool=False)->str:
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
        if fails - raise JSON error
    """
    output = None
    try:
        if indent > 0:
            output = json.dumps(content, indent=indent)
        else:
            output = json.dumps(content)
    except Exception as error:
        if exception is True:
            raise json.JSONDecodeError(msg=f"Failed to convert content into serialized JSON format (Error: {error})",
                                       doc=str(content), pos=0)

    return output


def check_conn_info(conn:str)->bool:
    """
    Check whether connection is correct format
    :args:
        conn:str - REST connection IP:Port
    :params:
        pattern:str - pattern to check connection is correct format
    :return:
        if fails then raise an error
        else - True
    """
    pattern1 = r'^(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}$'
    pattern2 = f'^(?:[a-zA-Z0-9._%+-]+(?::[a-zA-Z0-9._%+-]+)?@)?{pattern1}'

    if not re.match(pattern1, conn) and not re.match(pattern2, conn):
        raise ValueError('Connection information not in correct format - example [IP_Address]:[ANYLOG_REST_PORT]')

    return True

def separate_conn_info(conn:str)->(str, tuple):
    """
    Separate connection information provided
    :args:
        conn:str - REST connection information
    :params:
        pattern:str - pattern information
        auth:tuple - authentication information
    :return:
        conn, auth
    """
    pattern1 = r'^(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}$'
    pattern = f'^(?:[a-zA-Z0-9._%+-]+(?::[a-zA-Z0-9._%+-]+)?@)?{pattern1}'
    auth = ()
    if re.match(pattern, conn) is True or '@' in conn:
        auth, conn = conn.split('@')
        auth = tuple(auth.split(":"))

    return conn, auth


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
    time_interval_pattern = r'^\d*\s*(second|seconds|minute|minutes|hour|hours|day|days|month|months|year|years)$'

    if not bool(re.match(time_interval_pattern, time_interval.strip())):
        if exception is True:
            raise ValueError(f"Interval value {time_interval} - time interval options: second, minute, day, month or year")
        status = False

    return status
