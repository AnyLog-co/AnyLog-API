import anylog_api.anylog_connector as anylog_connector
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.generic.get import get_help


def set_authentication(conn:anylog_connector.AnyLogConnector, enable_auth:bool=False, destination:str=None,
                       view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    set authentication off / on - code will not work in EdgeLake
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        enable_auth:bool - whether to enable authentication
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status;bool - command status
        headers:dict - REST headers
    :return:
        None - if not executed
        True - if success
        False - if fails
    """
    status = None
    headers = {
        "command": f"set authentication off",
        "User-Agent": "AnyLog/1.23"
    }
    if enable_auth is True:
        headers['command'] = headers['command'].replac('off', 'on')
    if destination is not None:
        headers['destination'] = destination

    elif view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)
    return status
