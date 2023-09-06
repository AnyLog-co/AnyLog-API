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


def get_status(anylog_conn:AnyLogConnector, cmd_explain:bool=False, exception:bool=False):
    """
    Execute `get status` command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-status-command
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
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
    status = None
    headers = {
        "command": "get status where format=json",
        "User-Agent": "AnyLog/1.23"
    }

    if cmd_explain is True:
        get_help(anylog_conn=anylog_conn, cmd=headers["command"], exception=exception)
    else:
        status = False
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


def get_dictionary(anylog_conn:AnyLogConnector, is_json:bool=True, cmd_explain:bool=False, exception:bool=False):
    """
    Get dictionary from AnyLog
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-dictionary-command
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        is_json:bool - return results in JSON format
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
        "User-Agent": "AnyLog/1.23"
    }
    if is_json is True:
        headers["command"] += " where format=json"

    if cmd_explain is True:
        get_help(anylog_conn=anylog_conn, cmd=headers["command"], exception=exception)
    else:
        r, error = anylog_conn.get(headers=headers)
        if r is False and exception is True:
            print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif r is not False:
            dictionary = extract_results(cmd=headers['command'], r=r, exception=exception)
        return dictionary

    return None

