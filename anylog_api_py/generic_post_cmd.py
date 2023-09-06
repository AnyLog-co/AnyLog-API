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

