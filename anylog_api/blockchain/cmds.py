import anylog_api.anylog_connector  as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.generic.get import get_dictionary
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.__support__ import add_conditions, check_interval


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


def get_new_policy(conn:anylog_connector.AnyLogConnector, destination:str="", view_help:bool=False,
                   return_cmd:bool=False, exception:bool=False):
    """
    Get new policy from dictionary
    :args:
        conn:anylog_connector.AnyLogConnector - connection to
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
    dictionary = get_dictionary(conn=conn, json_format=True, destination=destination, view_help=view_help,
                                return_cmd=return_cmd, exception=exception)
    if 'new_policy' in dictionary:
        output = dictionary['new_policy']
    elif return_cmd is True:
        output = dictionary

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
    headers = {
        "command": f"blockchain seed from {ledger_conn}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, headers=headers, payload=None, exception=exception)

    return status


def blockchain_sync(conn:anylog_connector.AnyLogConnector, source:str=None, dest:str=None, time_interval:str=None,
                    ledger_conn:str=None, destination:str="", view_help:bool=False, return_cmd:bool=False,
                    exception:bool=False):
    """
    (Repeatedly) update the local copy of the blockchain
    :args:
        conn:anylog_connector.AnyLogConnector - connection to
        source:str - The source of the metadata
        dest:str - The destination of the blockchain data
        time_interval:str - frequency of updates
        ledger_conn:str - ledger connection information for master node use TCP IP:PORT (used for connection value)
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
    headers = {
        "command": f"run blockchain sync",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    if check_interval(time_interval=time_interval, exception=exception) is False:
        return status

    add_conditions(headers=headers, source=source, time=time_interval, dest=dest, connection=ledger_conn)

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, headers=headers, payload=None, exception=exception)

    return status


def reload_metadata(conn:anylog_connector.AnyLogConnector, destination:str="", view_help:bool=False,
                    return_cmd:bool=False, exception:bool=False):
    """
    Recreate the internal representation of the metadata from a local JSON file
    :args:
        conn:anylog_connector.AnyLogConnector - connection to
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
    headers = {
        "command": f"blockchain reload metadata",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, headers=headers, payload=None, exception=exception)

    return status


def prepare_policy(conn:anylog_connector.AnyLogConnector, policy:str, destination:str="", view_help:bool=False,
                   return_cmd:bool=False, exception:bool=False):
    """
    Prepare policy to be published
    :args:
        conn:anylog_connector.AnyLogConnector - connection to
        policy:str - policy to publish
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
    headers = {
        "command": "blockchain prepare policy !new_policy",
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, headers=headers, payload=f"<new_policy={policy}>", exception=exception)

    return status


def publish_policy(conn:anylog_connector.AnyLogConnector, policy:str, ledger_conn:str=None, local:bool=True,
                   destination:str="", view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    publish policy
    :args:
        conn:anylog_connector.AnyLogConnector - connection to
        policy:str - policy to publish
        ledger_conn:str - ledger connection information for master node use TCP IP:PORT
        local:bool - store policy on local blockchain
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
    headers = {
        "command": "blockchain insert",
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    add_conditions(headers, policy="!new_policy", local=local, master=ledger_conn)

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, headers=headers, payload=f"<new_policy={policy}>", exception=exception)

    return status








