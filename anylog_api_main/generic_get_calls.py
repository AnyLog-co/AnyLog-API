# Generic GET:  https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#get-command

from anylog_connector import AnyLogConnector
import rest_support









def get_network_info(anylog_conn:AnyLogConnector, json_format:bool=True, view_help:bool=False, exception:bool=False)->str:
    """
    Get network information
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        json_format:bool - whether to get results in JSON format
        view_help:bool - whether to get help info for command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        connections:dict - dict of AnyLog processes
        r:bool, error:str - whether the command failed & why
    :return:
        connections
    """
    connections = {}
    header={
        'command': 'get connections',
        'User-Agent': 'AnyLog/1.23'
    }

    if json_format is True:
        header['command'] += ' where format=json'

    if view_help is True:
        help_command(anylog_conn=anylog_conn, command=header['command'], exception=exception)
        connections = None
    else:
        r, error = anylog_conn.get(header=header)
        if r is False:
            if exception is True:
                rest_support.print_rest_error(call_type='GET', cmd=header['command'], error=error)
        elif not isinstance(r, bool):
            connections = rest_support.extract_results(cmd=header['command'], r=r, exception=exception)

    return connections




def get_operator(anylog_conn:AnyLogConnector, view_help:bool=False, exception:bool=False)->str:
    """
    view data comming into operator node
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20calls.md#get-operator
    :args:
        anylog_conn:AnyLogConnector - connect to AnyLog via REST
        view_help:bool - whether to print help information
        exception:bool - whether to print exceptions
    :params:
        output:str - output from GET request
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        output
    """
    output = None
    headers = {
        'command': 'get operator',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        r, error = anylog_conn.get(headers=headers)
        if r is False and exception is True:
            rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            output = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    return output


def get_publisher(anylog_conn:AnyLogConnector, view_help:bool=False, exception:bool=False)->str:
    """
    view data coming into publisher node
    :args:
        anylog_conn:AnyLogConnector - connect to AnyLog via REST
        view_help:bool - whether to print help information
        exception:bool - whether to print exceptions
    :params:
        output:str - output from GET request
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        output
    """
    output = None
    headers = {
        'command': 'get publisher',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        r, error = anylog_conn.get(headers=headers)
        if r is False and exception is True:
            rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            output = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    return output


def get_streaming(anylog_conn:AnyLogConnector, json_format:bool=True, view_help:bool=False, exception:bool=False)->str:
    """
    view streaming
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20calls.md#get-streaming
    :args:
        anylog_conn:AnyLogConnector - connect to AnyLog via REST
        json_Format:bool - get results in JSON format
        view_help:bool - whether to print help information
        exception:bool - whether to print exceptions
    :params:
        output:str - output from GET request
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        output
    """
    output = None
    headers = {
        'command': 'get streaming',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        if json_format is True:
            headers['command'] += ' where format=json'

        r, error = anylog_conn.get(headers=headers)
        if r is False and exception is True:
            rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            output = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    return output

