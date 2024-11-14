"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""

import json
import os.path
import re

import dotenv

import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_dictionary

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
        if indent > 0:
            output = json.dumps(content, indent=indent)
        else:
            output = json.dumps(content)
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
    for key, value in conditions.items():
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
    time_interval_pattern = r'^\d*\s*(second|seconds|minute|minutes|hour|hours|day|days|month|months|year|years)$'

    if not bool(re.match(time_interval_pattern, time_interval.strip())):
        if exception is True:
            print(f"Interval value {time_interval} - time interval options: second, minute, day, month or year")
        status = False

    return status


def check_email(email:str, exception:bool=False)->bool:
    """
    Check whether email is valid
    :args:
        email:str - user defined email
        exception:bool - whether to print exception
    :params:
        status:bool
        email_pattern:str - supported pattern
    :return:
        True - valid email
        False - invalid email
    """
    status = True
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    if not bool(re.match(email_pattern, email.strip())):
        status = False
        if exception is True:
            print(f"Invalid email format")

    return status


def get_generic_params(conn:anylog_connector.AnyLogConnector, exception:bool=False):
    """
    get default configuration values
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog
        exception:bool - whether to print exceptions
    :params:
        env_values:dict - Env Values
        config_file:str - configuration file
        default_configs:dict - configuration from AnyLog/EdgeLake dict
    :return:
        default_configs
    """
    env_values = None
    config_file = os.path.join(os.path.expanduser(os.path.expandvars(os.path.dirname(__file__))), 'default_configs.env')
    default_configs = get_dictionary(conn=conn, json_format=True, view_help=False, return_cmd=False, exception=exception)

    try:
        env_values = dotenv.dotenv_values(config_file)
    except Exception as error:
        if exception is True:
            print(f"Failed to extract content from default config file (Error: {error})")
    else:
        env_values = dict(env_values)

    if env_values is not None:
        for env_value in env_values:
            if env_value.lower() not in default_configs:
                default_configs[env_value.lower()] = env_values[env_value]

    return default_configs

