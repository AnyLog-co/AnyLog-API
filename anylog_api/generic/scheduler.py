import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.generic.post import execute_cmd


def run_scheduler1(conn:anylog_connector.AnyLogConnector, scheduler_id:int=1, destination:str=None,  return_cmd:bool=False,
                   view_help:bool=False, exception:bool=False):
    headers = {
        "command": f"run scheduler {scheduler_id}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']
    else:
        status = execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status
