import re

from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.rest_support import print_rest_error
from anylog_api_py.generic_get_cmd import get_help


def __validate_license_key(activation_key:str):
    """
    validate license key
    :args:
        activation_key:str - license key to validate
    :params:
        status:bool
        signature:UUID - AnyLog UUID license
        expiration;str - expiration date
        license_type;str - license type
    ;return:
        status
    """
    status = True
    signature = None
    expiration = None
    license_type = None

    if len(activation_key) <= 268:
        status = False
    else:
        signature = activation_key[:256]
        expiration = activation_key[256:266]
        license_type = activation_key[266]  # b for BETA and c for Commercial
    if signature is not None and not re.match(r'^[0-9a-fA-F]+$', signature):
        status = False
    if expiration is not None and not re.match("%Y-%m-%d", expiration):
        status = False
    if license_type not in ['c', 'b']:
        status = False

    return status


def enable_license_key(anylog_conn:AnyLogConnector, license_key:str, destination:str=None, cmd_explain:bool=False, exception:bool=False)->bool:
    """
    Enable license key
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#set-command
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        license_key:str - AnyLog key to use
        destination:str - destination IP:PORT
        exception:bool - whether to print exceptions or not
    """
    status = __validate_license_key(activation_key=license_key)
    headers = {
        "command": f"set license where activation_key={license_key}",
        "User-Agent": "AnyLog/1.23",
        "destination": destination
    }

    if cmd_explain is True:
        return get_help(anylog_conn=anylog_conn, cmd=headers['command'], exception=exception)
    elif status is False:
        if exception is True:
            print(f"Invalid license key...")
        return status

    r, error = anylog_conn.post(headers=headers, payload=None)
    if r is False:
        status = False
        if exception is True:
            print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status

def declare_configs(anylog_conn:AnyLogConnector, key:str, value:str, destination:str=None, cmd_explain:bool=False, exception:bool=False)->bool:
    """
    Declare params in AnyLog dictionary
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        key:str - key for value to be set by user
        value:str - value correlated to user
        destination:str - destination IP:PORT
        cmd_explain:bool - call help command instead of execute query
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
        "User-Agent": "AnyLog/1.23",
        "destination": destination
    }

    if not isinstance(value, str):
        headers["command"] = f"set {key}={value}"
    elif " " in value:
        headers["command"] = f'set {key.strip()}="{value.strip()}"'
    else:
        headers["command"] = f"set {key.strip()}={value.strip()}"

    if cmd_explain is True:
        return get_help(anylog_conn=anylog_conn, cmd=headers['command'], exception=exception)

    r, error = anylog_conn.post(headers=headers, payload=None)
    if r is False:
        status = False
        if exception is True:
            print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def declare_anylog_path(anylog_conn:AnyLogConnector, anylog_path:str, destination:str=None, cmd_explain:bool=False, exception:bool=False)->bool:
    """
    Declare the location of the root directory to the AnyLog Files.
    :url: 
        https://github.com/AnyLog-co/documentation/blob/master/getting%20started.md#switching-between-different-setups
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        anylog_path:str - path to set AnyLog in
        destination:str - destination IP:PORT
        cmd_explain:bool - call help command instead of execute query
        exception:bool - whether to print exceptions or not
    :params:
        status:bool
        headers:dict - REST header
    :return:
        status
    """
    status = True
    headers = {
        "command": f"set anylog home {anylog_path}",
        "User-Agent": "AnyLog/1.23",
        "destination": destination
    }
    if cmd_explain is True:
        return get_help(anylog_conn=anylog_conn, cmd=headers['command'], exception=exception)

    r, error = anylog_conn.post(headers=headers, payload=None)
    if r is False:
        status = False
        if exception is True:
            print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def create_work_directory(anylog_conn:AnyLogConnector, destination:str=None, cmd_explain:bool=False, exception:bool=False)->bool:
    """
    Create the work directories at their default locations or locations configured using "set anylog home" command
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/getting%20started.md#local-directory-structure
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        cmd_explain:bool - call help command instead of execute query
        destination:str - destination IP:PORT
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
        "User-Agent": "AnyLog/1.23",
        "destination": destination
    }
    if cmd_explain is True:
        return get_help(anylog_conn=anylog_conn, cmd=headers['command'], exception=exception)

    r, error = anylog_conn.post(headers=headers, payload=None)
    if r is False:
        status = False
        if exception is True:
            print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


