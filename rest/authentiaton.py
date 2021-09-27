import __init__
import anylog_api
import errors


def set_authentication_off(conn:anylog_api.AnyLogConnect, exception:bool=False)->bool:
    """
    Set authentication off - Authentication is off by default when deploying AnyLog
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        status:bool
        cmd:str - command to execute
    :return:
        status - True if no issues
    """
    status = False
    cmd = "set authentication off"
    r, error = conn.post(command=cmd)
    if not errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception):
        status = True
    return status


def set_node_id(conn:anylog_api.AnyLogConnect, auth:tuple=None, exception:bool=False)->bool:
    """
    Set node id if not exists
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        auth:tuple - authentication information
        exception:bool - whether to print exception
    :params:
        status:bool
        node_id:str - node id
        cmd:str - command to execute
    :return:
        status
    """
    status = True
    node_id = get_cmd.get_node_id(conn=conn, exception=exception)
    cmd = "id create keys for node where password=anylog"
    if auth is not None:
        cmd = "id create keys for node where password=%s" % auth[1]

    if node_id is None:
        r, error = conn.post(command=cmd)
        if errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception):
           status = False
        node_id = get_cmd.get_node_id(conn=conn, exception=exception)

    return node_id


def set_rest_authentication():
    """
    REST authentication
    """
    pass
