# Generic GET:  https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#get-command

from anylog_connector import AnyLogConnector
import rest_support


def get_status(anylog_conn:AnyLogConnector, json_format:bool=True, view_help:bool=False, exception:bool=False):
    """
    check if node is running
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-status-command
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        json_format:bool - whether to get the results in JSON format
        view_help:bool - whether to get help information for node
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
            if exception is True:
                rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            output = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)
            if isinstance(output, dict):
                output = output['Status']
            if 'running' in output and 'not' not in output:
                status = True

    return status


def get_license(anylog_conn:AnyLogConnector, view_help:bool=False, exception:bool=False):
    """
    Validate if license key
    :url:
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        view_help:bool - whether to get help information for node
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - has license key that's activated
        False - doesn't have a valid license key
        help - None
    """
    status = None
    headers = {
        "command": "get license",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        r, error = anylog_conn.get(headers=headers)
        if r is False:
            if exception is True:
                rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            output = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)
            if 'Status: Activation license is missing' not in output:
                status = True
            else:
                status = False

    return status

def get_dictionary(anylog_conn:AnyLogConnector, json_format:bool=True, view_help:bool=False, exception:bool=False):
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
        elif not isinstance(r, bool):
            anylog_dict = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    return anylog_dict


def get_processes(anylog_conn:AnyLogConnector, json_format:bool=True, view_help:bool=False, exception:bool=False):
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
        elif not isinstance(r, bool):
            processes_dict = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    return processes_dict


def get_network_info(anylog_conn:AnyLogConnector, json_format:bool=True, view_help:bool=False, exception:bool=False):
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


def get_hostname(anylog_conn:AnyLogConnector, view_help:bool=False, exception:bool=False):
    """
    Get hostname
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        view_help:bool - print help information for command
        exception:bool - whether to print exceptions
    :params:
        hostname:str - hostname
        headers:dict - REST header information
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
        elif not isinstance(r, bool):
            hostname = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    return hostname


def get_operator(anylog_conn:AnyLogConnector, view_help:bool=False, exception:bool=False):
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


def get_publisher(anylog_conn:AnyLogConnector, view_help:bool=False, exception:bool=False):
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


def get_streaming(anylog_conn:AnyLogConnector, json_format:bool=True, view_help:bool=False, exception:bool=False):
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
    elif not isinstance(r, bool):
        output = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    if output is not None:
        print(output)