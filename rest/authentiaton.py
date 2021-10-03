"""
Link: https://github.com/AnyLog-co/documentation/blob/master/authentication.md
"""
import __init__
import anylog_api
import get_cmd
import errors

HEADER = {
    "command": None,
    "User-Agent": "AnyLog/1.23"
}


def set_authentication_off(conn:anylog_api.AnyLogConnect, exception:bool=False)->bool:
    """
    Set authentication off - Authentication is off by default when deploying AnyLog
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        status:bool
        HEADER:dict - header for POST request
    :return:
        status - True if no issues
    """
    status = True
    HEADER['command'] = "set authentication off"
    r, error = conn.post(headers=HEADER)
    if errors.print_error(conn=conn.conn, request_type="post", command=HEADER['command'], r=r, error=error, exception=exception):
        status = False
    return status


def set_node_authentication(conn:anylog_api.AnyLogConnect, auth:tuple=None, exception:bool=False)->str:
    """
    Set node authentication
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        auth:tuple - authentication information
        exception:bool - whether to print exception
    :params:
        node_id:str - Node ID
        cmd:str - command to execute
        HEADER:dict - header for POST request
    :return:
        node id, if fails to set authentication or extract ID returns None
    """
    node_id = None
    cmd = "id create key for node where password=anylog"
    if auth is not None:
        cmd = cmd.replace('=anylog', '=%s' % auth[0])

    HEADER['command'] = cmd

    r, error = conn.post(headers=HEADER)
    if not errors.print_error(conn=conn.conn, request_type="post", command=cmd, r=r, error=error, exception=exception):
        node_id = get_cmd.get_node_id(conn=conn, exception=exception)

    return node_id