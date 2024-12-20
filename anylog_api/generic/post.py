"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
from typing import Union

import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import execute_publish_cmd
from concurrent.futures import ThreadPoolExecutor, as_completed



def set_params(conn:anylog_connector.AnyLogConnector, params:dict, destination:str=None, view_help:bool=False,
               exception:bool=False)->None:
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
        "command": "",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
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
                    raise Exception(f"Exception during command execution: {e}")



def set_node_name(conn:anylog_connector.AnyLogConnector, node_name:str, destination:str=None,
                  return_cmd:bool=False,  view_help:bool=False, exception:bool=False)->Union[bool,str,None]:
    """
    Sets a name that identifies the node
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
    headers = {
        "command": f"set node name {node_name}",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def set_path(conn:anylog_connector.AnyLogConnector, path:str, destination:str=None,  returnn_cmd:bool=False,
             view_help:bool=False, exception:bool=False)->Union[bool,str,None]:
    """
    Declare the location of the root directory to the AnyLog Files
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
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    elif returnn_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def disable_cli(conn:anylog_connector.AnyLogConnector, enable_cli:bool=False, destination:str=None,
                return_cmd:bool=False,  view_help:bool=False, exception:bool=False)->Union[bool,str,None]:
    """
    Disable the AnyLog CLI, when AnyLog is configured as a background process
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        enable_cli:bool - whether to enable the CLI (if disabled)
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
    headers = {
        "command": "set cli off",
        "User-Agent": "AnyLog/1.23"
    }

    if enable_cli is True:
        headers['command'] = headers['command'].replace('off', 'on')

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def create_work_dirs(conn:anylog_connector.AnyLogConnector, destination:str=None, return_cmd:bool=False,
                     view_help:bool=False, exception:bool=False)->Union[bool,str,None]:
    """
    Create the work directories at their default locations or locations configured using "set anylog home" command.
    The location of the directories is based on `set anylog home`
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
    headers = {
        "command": "create work directories",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status=headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def set_license_key(conn:anylog_connector.AnyLogConnector, license_key:str, destination:str=None, return_cmd:bool=False,
                     view_help:bool=False, exception:bool=False)->Union[bool,str,None]:
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
        output:str
        headers:dict - REST headers
    :return:
        None - if not executed
        True - if success
        False - if fails
    """
    headers = {
        "command": f"set license where activation_key={license_key}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return output


def reset_error_log(conn:anylog_connector.AnyLogConnector, destination:str=None, return_cmd:bool=False,
                    view_help:bool=False, exception:bool=False)->Union[bool,str,None]:
    """
    reset error log
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
    headers = {
        "command": "reset error log",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return output


def reset_event_log(conn:anylog_connector.AnyLogConnector, destination:str=None, return_cmd:bool=False,
                    view_help:bool=False, exception:bool=False)->Union[bool,str,None]:
    """
    reset event log
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
    headers = {
        "command": "reset event log",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return output


def set_echo_queue(conn:anylog_connector.AnyLogConnector, disable_queue:bool=False, destination:str=None,
                   return_cmd:bool=False, view_help:bool=False, exception:bool=False)->Union[bool,str,None]:
    """
    dis/enable echo queue
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        disable_queue:bool - whether to set echo queue off
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
    headers = {
        "command": "set echo queue on",
        "User-Agent": "AnyLog/1.23"
    }

    if disable_queue is True:
        headers['command'] += headers['command'].replace('on', 'off')

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return output


def reset_echo_queue(conn:anylog_connector.AnyLogConnector, destination:str=None, return_cmd:bool=False,
                     view_help:bool=False, exception:bool=False)->Union[bool,str,None]:
    """
    reset echo queue
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
    headers = {
        "command": "reset echo queue",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return output


def set_trace(conn:anylog_connector.AnyLogConnector, trace_level:int, cmd:str=None, destination:str=None,
              return_cmd:bool=False, view_help:bool=False, exception:bool=False)->Union[bool, str, None]:
    """
    Set trace level when commands comes into node
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        trace_level:int - level of trace
            * 0 - disable
            * 1 - 3 -- level of tracing
        cmd:str - specific command to trace
            Examples - rest, tcp, run client, etc...
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
    headers = {
        "command": f"trace level={int(trace_level)}",
        "User-Agent": "AnyLog/1.23"
    }
    if cmd:
        headers['command'] += f" {cmd}"

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return output

