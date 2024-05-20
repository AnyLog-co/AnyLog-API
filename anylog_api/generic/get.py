# URL https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#get-command

import anylog_api.anylog_connector as anylog_connector
from anylog_api.anylog_connector_support import extract_get_results


def get_help(conn:anylog_connector.AnyLogConnector, cmd:str=None, exception:bool=False):
    """
    Get help information about command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/getting%20started.md#the-help-command
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        cmd:str - command to get help with
        exception:bool - whether to print exception
    :params:
        output:str - results
        headers:dict - REST headers
    :output:
        prints help information for a given command
    """
    headers = {
        "command": "help",
        "User-Agent": "AnyLog/1.23",
    }
    if cmd is not None:
        headers['command'] += " " + cmd

    output = extract_get_results(conn=conn, headers=headers, exception=exception)
    print(output)


def get_status(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False, return_cmd:bool=False,
               exception:bool=False):
    """
    Check whether node is running
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-status-command
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status:bool - whether node is accessible
        headers:dict - REST headers
        output:str - results
    :return:
        None - prints help
        True - node accessible
        False - node not accessible
    """
    status = None
    headers = {
        "command": "get status where format=json",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']
    else:
        status = True
        output = extract_get_results(conn=conn, headers=headers, exception=exception)
        if isinstance(output, dict) and 'Status' in output and ('not' in output['Status'] or 'running' not in output['Status']):
            status = False
        elif isinstance(output, str) and ('not' in output or 'running' not in output):
            status = False

    return status


def get_dictionary(conn:anylog_connector.AnyLogConnector, json_format:bool=True, destination:str=None,
                   view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    get dictionary
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-dictionary-command
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
        "command": "get dictionary",
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


def get_node_name(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                  return_cmd:bool=False, exception:bool=False):
    """
    get node name
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#get-node-name
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
        "command": "get node name",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def get_hostname(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False):
    """
    get hostname
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
        "command": "get hostname",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def get_version(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                return_cmd:bool=False, exception:bool=False):
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
        "command": "get version",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output
