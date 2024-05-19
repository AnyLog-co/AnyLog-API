import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.generic.get import get_dictionary
from anylog_api.anylog_connector_support import execute_publish_cmd


def set_debug(conn:anylog_connector.AnyLogConnector, state:str='off', destination:str=None, view_help:bool=False,
              return_cmd:bool=False, exception:bool=False):
    """
    set debug (used mainly in scripts)
        - on
        - off
        - interactive
    :url:
       https://github.com/AnyLog-co/documentation/blob/master/cli.md#the-set-debug-command
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        state:str - debug state
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
        False - if fails / not ran
    """
    status = None
    headers = {
        "command": f"set debug {state}",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    if state not in ['on','off','interactive']:
        status = False
        if exception is True:
            print(f"Invalid value for state {state} (Options; on, off, interactive]")
    elif view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    elif return_cmd is True:
        return headers['command']
    else:
        status = execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


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
    if destination is not None:
        headers['destination'] = destination

    for key in params:
        headers['command'] = f'set {key} = {params[key]}'
        if view_help is True:
            get_help(conn=conn, cmd=headers['command'], exception=exception)
            break
        else:
            execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

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
        "command": f"set node {node_name}",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    elif return_cmd is True:
        return headers['command']
    else:
        status = execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def set_path(conn:anylog_connector.AnyLogConnector, path:str, destination:str=None,  returnn_cmd:bool=False,
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
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    elif returnn_cmd is True:
        return headers['command']
    else:
        status = execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

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
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    elif return_cmd is True:
        return headers['command']
    else:
        status = execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def create_work_dirs(conn:anylog_connector.AnyLogConnector, destination:str=None,  return_cmd:bool=False,
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
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']
    else:
        status = execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def execute_process(anylog_conn:AnyLogConnector, file_path:str, view_help:bool=False, exception:bool=False)->bool:
    """
    Execute an AnyLog file via REST - file must be accessible on the AnyLog instance
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/node%20configuration.md#the-configuration-process
    :args:
        anylog_conn:AnyLogConnector - AnyLog connection information
        file_path:str - file (on the AnyLog instance) to be executed
        view_help:bool - whether to print help
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - print help information
    """
    status = None
    headers = {
        'command': 'process',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status