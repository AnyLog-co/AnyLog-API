from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.rest_support import print_rest_error, extract_results


def get_status(anylog_conn:AnyLogConnector, exception:bool=False)->bool:
    """
    Execute `get status` command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-status-command
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        exception:bool - whether to print exceptions or not
    :params:
        status:bool
        header:dict - REST header
    :return:
        True if able to connect
        False if unable to connect
    """
    status = False
    headers = {
        "command": "get status where format=json",
        "User-Agent": "AnyLog/1.23"
    }

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


def get_dictionary(anylog_conn:AnyLogConnector, is_json:bool=True, exception:bool=False)->str:
    """
    Get dictionary from AnyLog
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-dictionary-command
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        is_json:bool - return results in JSON format
        exception:bool - whether to print exceptions or not
    :params:
        dictionary:dict - content in AnyLog dictionary
        headers:dict - REST headers
    :return:
        dictionary
    """
    dictionary = {}
    headers = {
        "command": "get dictionary",
        "User-Agent": "AnyLog/1.23"
    }
    if is_json is True:
        headers["command"] += " where format=json"

    r, error = anylog_conn.get(headers=headers)
    if r is False and exception is True:
        print_rest_error(call_type='GET', cmd=headers['command'], error=error)
    elif r is not False:
        dictionary = extract_results(cmd=headers['command'], r=r, exception=exception)

    return dictionary

