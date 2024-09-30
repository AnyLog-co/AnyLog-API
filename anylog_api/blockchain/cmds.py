import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
# from anylog_api.generic.get import get_dictionary
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.anylog_connector_support import extract_get_results
# from anylog_api.__support__ import add_conditions, check_interval

def get_policy(conn:anylog_connector.AnyLogConnector, policy_type:str='*', where_condition:str=None,
               bring_case:str=None, bring_condition:str=None, seperator:str=None, destination:str="",
               view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Generate & execute `blockchain get` command
    :sample queries:
        blockchain get *
        blockchain get (master, operator, query) where company = "My Company" bring.table [*] [*][name] [*][ip] [*][port]
    :args:
        conn:anylog_connector.AnyLogConnector - connection to
        policy_type:str - policy type
        where_condition:str - where condition(s)
        bring_case:str - bring case (ex. last / first / unique / sort)
        bring_condition:str - bring condition(s)
        separator:str - how to separator results
        destination:str - remote connection information
        view_help:bool - print help information
        return_cmd:bool - return command to be executed
        exception:bool - print exception
    :params:
        output - content returned
        headers:dict - REST header information
    :return:
        output
    """
    output = None
    headers = {
        "command": f"blockchain get {policy_type}",
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    if where_condition:
            headers['command'] += f" where {where_condition}"
    if bring_case:
        headers['command'] += f" bring.{bring_case}"
    if bring_condition and bring_case:
        headers['command'] += f" {bring_condition}"
    elif bring_condition:
        headers['command'] += f" bring {bring_condition}"
    if seperator:
        headers['command'] += f" separator='{seperator}'"

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def execute_seed(conn:anylog_connector.AnyLogConnector, ledger_conn:str, destination:str="", view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False):
    """
    Pull the metadata from a source node
    :args:
        conn:anylog_connector.AnyLogConnector - connection to
        ledger_conn:str - ledger connection information for master node use TCP IP:PORT
        destination:str - remote connection information
        view_help:bool - print help information
        return_cmd:bool - return command to be executed
        exception:bool - print exception
    :params:
        output - content returned
        headers:dict - REST header information
    :return:
        output
    """
    status = None
    cmd = None
    headers = {
        "command": f"blockchain seed from {ledger_conn}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        cmd = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd="POST", headers=headers, payload=None, exception=exception)

    return status, cmd