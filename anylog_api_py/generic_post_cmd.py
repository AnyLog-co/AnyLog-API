from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.rest_support import print_rest_error


def declare_configs(anylog_conn:AnyLogConnector, key:str, value:str, exception:bool=False)->bool:
    """
    Declare params in AnyLog dictionary
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        key:str - key for value to be set by user
        value:str - value correlated to user
        exception:bool - whether to print exceptions or not
    :params:
        status:bool
        headers:dict - REST header
    :return:
        status
    """
    status = True
    headers = {
        "command": "",
        "User-Agent": "AnyLog/1.23"
    }

    if not isinstance(value, str):
        headers["command"] = f"set {key}={value}"
    elif " " in value:
        headers["command"] = f'set {key.strip()}="{value.strip()}"'
    else:
        headers["command"] = f"set {key.strip()}={value.strip()}"

    r, error = anylog_conn.post(headers=headers, payload=None)
    if r is False:
        status = False
        if exception is True:
            print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def declare_anylog_path(anylog_conn:AnyLogConnector, anylog_path:str, exception:bool=False)->bool:
    """
    Declare the location of the root directory to the AnyLog Files.
    :url: 
        https://github.com/AnyLog-co/documentation/blob/master/getting%20started.md#switching-between-different-setups
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        anylog_path:str - path to set AnyLog in
        exception:bool - whether to print exceptions or not
    :params:
        status:bool
        headers:dict - REST header
    :return:
        status
    """
    headers = {
        "command": f"set anylog home {anylog_path}",
        "User-Agent": "AnyLog/1.23"
    }

    r, error = anylog_conn.post(headers=headers, payload=None)
    if r is False:
        status = False
        if exception is True:
            print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def create_work_directory(anylog_conn:AnyLogConnector, exception:bool=False)->bool:
    """
    Create the work directories at their default locations or locations configured using "set anylog home" command
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/getting%20started.md#local-directory-structure
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        exception:bool - whether to print exceptions or not
    :params:
        status:bool
        headers:dict - REST headers
    :return:
        status
    """
    status = True
    headers = {
        "command": "create work directories",
        "User-Agent": "AnyLog/1.23"
    }

    r, error = anylog_conn.post(headers=headers, payload=None)
    if r is False:
        status = False
        if exception is True:
            print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


