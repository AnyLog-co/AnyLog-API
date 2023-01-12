# Generic GET:  https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#get-command

from anylog_connector import AnyLogConnector
import rest_support


def get_status(anylog_conn:AnyLogConnector, json_format:bool=True, view_help:bool=False, exception:bool=False)->bool:
    """
    check if node is running
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-status-command
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        json_format:bool - whether to get the results in JSON format
        view_:bool - whether to get help information for node
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - running
        False - not running
        help - None
    """
    status = None
    output = None
    headers = {
        'command': 'get status',
        'User-Agent': 'AnyLog/1.23'
    }

    if json_format is True:
        headers['command'] += f' where format=json'

    if view_help is True:
        help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        r, error = anylog_conn.get(headers=headers)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif r is not False:
            output = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)
            if isinstance(output, dict):
                output = output['status']
            if 'running' in output and 'not' not in output:
                status = True
            else:
                status = False

    return status


def get_dictionary(anylog_conn:AnyLogConnector, json_format:bool=True, view_help:bool=False, exception:bool=False)->dict:
    """
    Extract AnyLog dictionary
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-dictionary-command
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        json_format:bool - whether to get results in JSON-dict format
        view_help:bool - whether to view help for given command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header
        anylog_dict:dict - results for dictionary
        r:bool, error:str - whether the command failed & why
    :return:
        anylog_dict - empty dict if nothing gets returned or help is executed
    """
    anylog_dict = {}
    headers = {
        'command': 'get dictionary',
        'User-Agent': 'AnyLog/1.23'
    }
    if json_format is True:
        headers['command'] += ' where format=json'

    if view_help is True:
        help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        r, error = anylog_conn.get(headers=headers)
        if r is False and exception is True:
            rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif r is not False:
            anylog_dict = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    return anylog_dict


def get_processes(anylog_conn:AnyLogConnector, json_format:bool=True, view_help:bool=False, exception:bool=False)->dict:
    """
    view running / not declared processes
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-processes-command
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        json_format:bool - whether to get results in JSON format
        view_help:bool - whether to get help info for command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        processes_dict - dict of AnyLog processes
        r:bool, error:str - whether the command failed & why
    :return:
        processes_dict
    """
    processes_dict = {}
    headers = {
        'command': 'get processes',
        'User-Agent': 'AnyLog/1.23'
    }

    if json_format is True:
        headers['command'] += ' where format=json'

    if view_help is True:
        help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        r, error = anylog_conn.get(headers=headers)
        if r is False and exception is True:
            rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif r is not False:
            processes_dict = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    return processes_dict


def get_hostname(anylog_conn:AnyLogConnector, view_help:bool=False, exception:bool=False)->str:
    """
    Get hostname
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        view_help:bool - print help information for command
        exception:bool - whether to print exceptions
    :params:
        hostname:str - hostname
        processes_dict - dict of AnyLog processes
        r:bool, error:str - whether the command failed & why
    :return:
        hostname
    """
    hostname = None
    headers = {
        'command': 'get hostname',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        r, error = anylog_conn.get(headers=headers)
        if r is False and exception is True:
            rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif r is not False:
            hostname = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    return hostname


def help_command(anylog_conn:AnyLogConnector, command:str=None, exception:bool=False):
    """
    Given a command, get the `help` output for it
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/getting%20started.md#the-help-command
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        command:str - command to get help for
        exception:bool - whether to print exceptions
    :params:
        output:str - help information
        headers:dict - REST header information
        r:requests.get, error - output for GET request
    :print:
        prints the results for `help` command
    """
    output = None
    headers = {
        'command': 'help',
        'User-Agent': 'AnyLog/1.23'
    }
    if command is not None:
        headers['command'] += f' {command}'

    r, error = anylog_conn.get(headers=headers)
    if r is False:
        if exception is True:
            rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
    else:
        output = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    if output is not None:
        print(output)