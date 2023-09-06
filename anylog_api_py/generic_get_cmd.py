from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.rest_support import print_rest_error, extract_results


def get_help(anylog_conn:AnyLogConnector, cmd:str, exception:bool=False):
    """
    Provide information about an AnyLog command
    :URL:
         https://github.com/AnyLog-co/documentation/blob/master/getting%20started.md#the-help-command
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        cmd:str - command to get information for
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST headers
    :print:
        help information
    """
    headers = {
        "command": f"help {cmd}",
        "User-Agent": "AnyLog/1.23"
    }

    r, error = anylog_conn.get(headers=headers)
    if r is False and exception is True:
        print_rest_error(call_type='GET', cmd=headers['command'], error=error)
    elif r is not False:
        print(extract_results(cmd=headers['command'], r=r, exception=exception))

    return None


def get_status(anylog_conn:AnyLogConnector, destination:str=None, cmd_explain:bool=False, exception:bool=False):
    """
    Execute `get status` command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-status-command
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        destination:str - destination IP:PORT
        cmd_explain:bool - call help command instead of execute query
        exception:bool - whether to print exceptions or not
    :params:
        status:bool
        header:dict - REST header
    :return:
        True if able to connect
        False if unable to connect
        None if get_help
    """
    status = False
    headers = {
        "command": "get status where format=json",
        "User-Agent": "AnyLog/1.23",
        "destination": destination
    }

    if cmd_explain is True:
        return get_help(anylog_conn=anylog_conn, cmd=headers["command"], exception=exception)

    r, error = anylog_conn.get(headers=headers)
    if r is False and exception is True:
        print_rest_error(call_type='GET', cmd=headers['command'], error=error)
    elif r is not False:
        try:
            if 'running' in extract_results(cmd=headers['command'], r=r, exception=exception)['Status']:
                status = True
        except Exception as error:
            if exception is True:
                print(f"Failed to extract results for `{headers['command']}` (Error: {error})")

    return status


def get_event_log(anylog_conn:AnyLogConnector, json_format:bool=True, destination:str=None, cmd_explain:bool=False, exception:bool=False):
    """
    recently executed commands
    :URL:
         https://github.com/AnyLog-co/documentation/blob/master/logging%20events.md#the-event-log
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        destination:str - destination IP:PORT
        json_format:bool - print results in JSON format
        cmd_explain:bool - call help command instead of execute query
        exception:bool - whether to print exceptions or not
    """
    output = None
    headers = {
        "command": "get event log",
        "User-Agent": "AnyLog/1.23",
        "destination": destination
    }
    if json_format is True:
        headers["command"] += " where format=json"

    if cmd_explain is True:
        return get_help(anylog_conn=anylog_conn, cmd=headers["command"], exception=exception)

    r, error = anylog_conn.get(headers=headers)
    if r is False and exception is True:
        print_rest_error(call_type='GET', cmd=headers['command'], error=error)
    elif r is not False:
        output = extract_results(cmd=headers['command'], r=r, exception=exception)

    return output


def get_error_log(anylog_conn:AnyLogConnector, json_format:bool=True, destination:str=None, cmd_explain:bool=False,exception:bool=False):
    """
    recently shown errors
    :URL:
         https://github.com/AnyLog-co/documentation/blob/master/logging%20events.md#the-error-log
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        json_format:bool - print results in JSON format
        destination:str - destination IP:PORT
        cmd_explain:bool - call help command instead of execute query
        exception:bool - whether to print exceptions or not
    """
    output = None
    headers = {
        "command": "get error log",
        "User-Agent": "AnyLog/1.23",
        "destination": destination
    }
    if json_format is True:
        headers["command"] += " where format=json"

    if cmd_explain is True:
        return get_help(anylog_conn=anylog_conn, cmd=headers["command"], exception=exception)

    r, error = anylog_conn.get(headers=headers)
    if r is False and exception is True:
        print_rest_error(call_type='GET', cmd=headers['command'], error=error)
    elif r is not False:
        output = extract_results(cmd=headers['command'], r=r, exception=exception)

    return output


def get_echo_queue(anylog_conn:AnyLogConnector, destination:str=None, cmd_explain:bool=False, exception:bool=False):
    """
    Get the echo commands from the current nodes and peer nodes.
    :URL:
         https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#get-command
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        destination:str - destination IP:PORT
        cmd_explain:bool - call help command instead of execute query
        exception:bool - whether to print exceptions or not
    """
    output = None
    headers = {
        "command": "get echo queue",
        "User-Agent": "AnyLog/1.23",
        "destination": destination
    }

    if cmd_explain is True:
        return get_help(anylog_conn=anylog_conn, cmd=headers["command"], exception=exception)

    r, error = anylog_conn.get(headers=headers)
    if r is False and exception is True:
        print_rest_error(call_type='GET', cmd=headers['command'], error=error)
    elif r is not False:
        output = extract_results(cmd=headers['command'], r=r, exception=exception)

    return output


def get_dictionary(anylog_conn:AnyLogConnector, destination:str=None, is_json:bool=True, cmd_explain:bool=False, exception:bool=False):
    """
    Get dictionary from AnyLog
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-dictionary-command
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        is_json:bool - return results in JSON format
        destination:str - destination IP:PORT
        cmd_explain:bool - call help command instead of execute query
        exception:bool - whether to print exceptions or not
    :params:
        dictionary:dict - content in AnyLog dictionary
        headers:dict - REST headers
    :return:
        dictionary
        help returns None
    """
    dictionary = {}
    headers = {
        "command": "get dictionary",
        "User-Agent": "AnyLog/1.23",
        "destination": destination
    }
    if is_json is True:
        headers["command"] += " where format=json"

    if cmd_explain is True:
        return get_help(anylog_conn=anylog_conn, cmd=headers["command"], exception=exception)

    r, error = anylog_conn.get(headers=headers)
    if r is False and exception is True:
        print_rest_error(call_type='GET', cmd=headers['command'], error=error)
    elif r is not False:
        dictionary = extract_results(cmd=headers['command'], r=r, exception=exception)
    return dictionary



