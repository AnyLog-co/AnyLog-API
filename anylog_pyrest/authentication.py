"""
URL: https://github.com/AnyLog-co/documentation/blob/master/authentication.md
"""
from anylog_connection import AnyLogConnection
from support import print_error

def disable_authentication(anylog_conn:AnyLogConnection, exception:bool=False)->bool:
    """
    disable authentication
    :params:
        set authentication off
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        headers:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    headers = {
        "command": "set authentication off",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def get_node_id(anylog_conn:AnyLogConnection, exception:bool=False)->str:
    """
    disable authentication
    :params:
        get node id
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        output:str - placeholder containing Node ID extracted via REST
        headers:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    output = None
    headers = {
        "command": "get node id",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(error_type="GET", cmd=headers['command'], error=error)
    elif int(r.status_code) == 200:
        try:
            output = r.text
        except Exception as e:
            r = False
            if exception is Ture:
                print(f"Failed to extract NODE ID (Error: {e})")
        else:
            r = output
    return r


