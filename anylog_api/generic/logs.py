import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.anylog_connector_support import execute_publish_cmd


def reset_error_log(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                    return_cmd:bool=False, exception:bool=False):
    """
    reset error logs
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status:bool - command status
        headers:dict - REST headers
    :return:
        None - if not executed
        True - if success
        False - if fails
    """
    status = None
    headers = {
        "command": f"reset error log",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def reset_event_log(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                    return_cmd:bool=False, exception:bool=False):
    """
    reset event logs
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status:bool - command status
        headers:dict - REST headers
    :return:
        None - if not executed
        True - if success
        False - if fails
    """
    status = None
    headers = {
        "command": f"reset event log",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def set_echo_queue(conn:anylog_connector.AnyLogConnector, enable_echo_queue:bool=True, destination:str=None, view_help:bool=False,
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
        "command": f"set echo queue on",
        "User-Agent": "AnyLog/1.23"
    }
    if enable_echo_queue is False:
        headers['command'] = headers['command'].replace("on", "off")

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)
    return status


def reset_echo_queue(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                     return_cmd:bool=False, exception:bool=False):
    """
    delete everything from echo queue
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status:bool - command status
        headers:dict - REST headers
    :return:
        None - if not executed
        True - if success
        False - if fails
    """
    status = None
    headers = {
        "command": f"reset echo queue",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)
    return status


def echo_msg(conn:anylog_connector.AnyLogConnector, msg:str, destination:str=None, view_help:bool=False,
             return_cmd:bool=False, exception:bool=False):
    """
    send message to echo queue
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        message:str - Message to send
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status:bool - command status
        headers:dict - REST headers
    :return:
        None - if not executed
        True - if success
        False - if fails
    """
    status = None
    headers = {
        "command": f"echo {msg}",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)
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
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
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
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
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
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def get_processes(conn:anylog_connector.AnyLogConnector, json_format:bool=True, destination:str=None,
                  return_cmd:bool=False, view_help:bool=False, exception:bool=False):
    """
    view running / not declared processes
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-processes-command
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status:bool
        processes_dict - dict of AnyLog processes
        r:bool, error:str - whether the command failed & why
    :return:
        processes_dict
    """
    output = None
    headers = {
        'command': 'get processes',
        'User-Agent': 'AnyLog/1.23'
    }

    if json_format is True:
        headers['command'] += " where format=json"
    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output

