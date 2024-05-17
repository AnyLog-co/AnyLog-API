import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import extract_get_results
from anylog_api.generic.post import execute_cmd
from anylog_api.generic.get import get_help


def set_echo_queue(conn:anylog_connector.AnyLogConnector, state:str='on', destination:str=None, view_help:bool=False,
                   return_cmd:bool=False, exception:bool=False):
    """
    set echo queue
        - on
        - off
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
    elif return_cmd is True:
        return headers['command']
    else:
        status = execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)
    return status


def get_error_log(conn:anylog_connector.AnyLogConnector, json_format:bool=False, destination:str=None,
                  return_cmd:bool=False,  view_help:bool=False, exception:bool=False):
    """
    get error log
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/logging%20events.md#the-error-log
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        headers:dict - REST headers
        output:str - results
    :return:
        headers
    """
    output = None
    headers = {
        "command": "get error log",
        "User-Agent": "AnyLog/1.23"
    }

    if json_format is True:
        headers['command'] += " where format=json"
    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    elif return_cmd is True:
        output = headers['command']
    else:
        status = True
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def get_event_log(conn:anylog_connector.AnyLogConnector, json_format:bool=False, destination:str=None,
                  return_cmd:bool=False,  view_help:bool=False, exception:bool=False):
    """
    get error log
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/logging%20events.md#the-error-log
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        headers:dict - REST headers
        output:str - results
    :return:
        headers
    """
    output = None
    headers = {
        "command": "get error log",
        "User-Agent": "AnyLog/1.23"
    }

    if json_format is True:
        headers['command'] += " where format=json"
    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    elif return_cmd is True:
        output = headers['command']
    else:
        status = True
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def get_echo_queue(conn:anylog_connector.AnyLogConnector, json_format:bool=False, destination:str=None,
                   return_cmd:bool=False,  view_help:bool=False, exception:bool=False):
    """
    get echo queue
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        headers:dict - REST headers
        output:str - results
    :return:
        output
    """
    output = None
    headers = {
        "command": "get error log",
        "User-Agent": "AnyLog/1.23"
    }

    if json_format is True:
        headers['command'] += " where format=json"
    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        status = True
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


