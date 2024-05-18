import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.generic.post import execute_cmd

def connect_dbms(conn:anylog_connector.AnyLogConnector, db_name:str, db_type:str='sqlite', host:str=None, port:int=None,
                 user:str=None, password:str=None, memory:bool=False, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False):

    headers = {
        "command": f"connect dbms {db_name} where type={db_type}",
        "User-Agent": "AnyLog/1.23"
    }

    if host:
        headers['command'] += f" and ip={host}"
    if port:
        headers['command'] += f" and port={port}"
    if user:
        headers['command'] += f" and user={user}"
    if password:
        headers['command'] += f" and password={password}"
    if memory is True and db_name == 'sqlite':
        headers['command'] += f" and memory=true"

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']
    else:
        status = execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status
