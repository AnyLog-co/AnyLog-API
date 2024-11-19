"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""

import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import execute_publish_cmd
from concurrent.futures import ThreadPoolExecutor, as_completed



def set_params(conn:anylog_connector.AnyLogConnector, params:dict, destination:str=None, view_help:bool=False,
               exception:bool=False):
    """
    add dictionary param
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        params:dict - dictionary of key / value pairs to set node with
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        headers:dict - REST head information
    """
    headers = {
        "command": None,
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    # Define a function to handle the command execution for each key-value pair
    def execute_command(key, value):
        if value in ['false', 'False', 'True', 'true', 'file']:
            command = f'set {key.strip()} = {value.strip()}'
        elif value != "":
            command = f'{key.strip()} = {value.strip()}'
        else:
            return  # Skip empty values
        headers['command'] = command

        if view_help:
            get_help(conn=conn, cmd=command, exception=exception)
        else:
            execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    # Use ThreadPoolExecutor with a maximum of 10 threads
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit each command as a task to the executor
        futures = [executor.submit(execute_command, key, params[key]) for key in params]

        # Wait for all futures to complete
        for future in as_completed(futures):
            # Optionally handle any exceptions
            try:
                future.result()  # We could check results or exceptions here if needed
            except Exception as e:
                if exception:
                    raise Exception(f"Exception during command execution:{e}")



def set_node_name(conn:anylog_connector.AnyLogConnector, node_name:str, destination:str=None,
                  return_cmd:bool=False,  view_help:bool=False, exception:bool=False):
    """
    Set node name
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        node_name:str - node name
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status;bool - command status
        headers:dict - REST headers
    :return:
        None - if not executed
        True - if success
        False - if fails
    """
    status = None
    headers = {
        "command": f"set node name {node_name}",
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']
    elif return_cmd is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def set_anylog_home(conn:anylog_connector.AnyLogConnector, path:str, destination:str=None,  return_cmd:bool=False,
             view_help:bool=False, exception:bool=False):
    """
    Set root path
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        path:str - root directory path
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status;bool - command status
        headers:dict - REST headers
    :return:
        None - if not executed
        True - if success
        False - if fails
    """
    status = None
    headers = {
        "command": f"set anylog home {path}",
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    elif return_cmd is True:
        return headers['command']
    elif return_cmd is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def disable_cli(conn:anylog_connector.AnyLogConnector, destination:str=None,  return_cmd:bool=False,  view_help:bool=False, exception:bool=False):
    """
    Disable the CLI
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status;bool - command status
        headers:dict - REST headers
    :return:
        None - if not executed
        True - if success
        False - if fails
    """
    status = None
    headers = {
        "command": "set cli off",
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']
    elif return_cmd is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def create_work_dirs(conn:anylog_connector.AnyLogConnector, destination:str=None, return_cmd:bool=False,
                     view_help:bool=False, exception:bool=False):
    """
    create work directories
    :tree:
    /app
    ├── EdgeLake                        [Directory containing authentication keys and passwords]
    │   ├── blockchain                  [A JSON file representing the metadata relevant to the node]
    │   └── data                        [Users data and intermediate data processed by this node]
    │       ├── archive                 [The root directory of and archival directory]
    │       ├── bkup                    [Optional location for backup of user data]
    │       ├── blobs                   [Directory containing unstructured data]
    │       ├── dbms                    [Optional location for persistent database data. If using SQLite, used for persistent SQLIte data]
    │       ├── distr                   [Directory used in the High Availability processes]
    │       ├── error                   [The storage location for new data that failed database storage]
    │       ├── pem                     [Directory containing keys and certificates]
    │       ├── prep                    [Directory for system intermediate data]
    │       ├── test                    [Directory location for output data of test queries]
    │       ├── watch                   [Directory monitored by the system, data files placed in the directory are being processed]
    │       └── bwatch                  [Directory monitored by the system, managing unstructured data]
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status;bool - command status
        headers:dict - REST headers
    :return:
        None - if not executed
        True - if success
        False - if fails
    """
    status = None
    headers = {
        "command": "create work directories",
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']
    elif return_cmd is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def set_license_key(conn:anylog_connector.AnyLogConnector, license_key:str, destination:str=None, return_cmd:bool=False,
                     view_help:bool=False, exception:bool=False):
    """
    Set license key for AnyLog node
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        license_key:str - license key to be used
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status;bool - command status
        headers:dict - REST headers
    :return:
        None - if not executed
        True - if success
        False - if fails
    """
    status = None
    headers = {
        "command": f"set license where activation_key={license_key}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']
    elif return_cmd is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status



