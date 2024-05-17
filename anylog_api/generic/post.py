import anylog_api.anylog_connector as anylog_connector
import anylog_api.anylog_connector_support as anylog_connector_support
from anylog_api.generic.get import get_help
"""
on error ignore
set debug off
set echo queue on
set authentication off
"""


def execute_cmd(conn:anylog_connector.AnyLogConnector, cmd:str, headers:dict, payload:str=None, exception:bool=False):
    """
    Execute command (both POST and PUT)
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        cmd:str - PUT or POST
        headers:dict - REST headers
        exception:bool - whether to print exception
    :params:
        status:bool - whether execution succeed or failed
    :return:
        output
    """
    status = True
    if cmd == 'post':
        r, error = conn.post(headers=headers, payload=payload)
    elif cmd == 'put':
        r, error = conn.put(headers=headers, payload=payload)

    if r is False:
        status = False
        if exception is True:
            anylog_connector_support.print_rest_error(call_type=cmd.upper(), cmd=headers['command'], error=error)
    return status


def set_debug(conn:anylog_connector.AnyLogConnector, state:str='off', destination:str=None, view_help:bool=False,
              exception:bool=False):
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
    else:
        status = execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)
    return status


def set_echo_queue(conn:anylog_connector.AnyLogConnector, state:str='on', destination:str=None, view_help:bool=False,
                   exception:bool=False):
    """
    set echo queue
        - on
        - off
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        state:str - debug state
        destination:str - Remote node to query against
        view_help:bool - get information about command
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
        "command": f"set echo queue {state}",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    if state not in ['on','off']:
        status = False
        if exception is True:
            print(f"Invalid value for state {state} (Options; on, off, interactive]")
    elif view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    else:
        status = execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)
    return status


def set_authentication(conn:anylog_connector.AnyLogConnector, state:str='on', destination:str=None, view_help:bool=False,
                       exception:bool=False):
    """
    set authentication
        - on
        - off
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        state:str - debug state
        destination:str - Remote node to query against
        view_help:bool - get information about command
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
        "command": f"set authentication {state}",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    if state not in ['on','off']:
        status = False
        if exception is True:
            print(f"Invalid value for state {state} (Options; on, off, interactive]")
    elif view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    else:
        status = execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)
    return status
