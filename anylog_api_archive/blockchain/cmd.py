"""
prepare
insert
delete
get
"""
import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.post import execute_cmd

def blockchain_sync(conn:anylog_connector.AnyLogConnector, source:str='master', time:str='30 seconds', dest:str='file',
                    connection:str='!ledger_conn', destination:str=None,  return_cmd:bool=False, view_help:bool=False,
                    exception:bool=False):
    """

    """
    headers = {
        "command": f"run blockchain sync where source={source} and time={time} and dest={dest} and connection={connection}",
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


