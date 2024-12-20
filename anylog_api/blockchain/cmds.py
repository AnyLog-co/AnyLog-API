"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
from typing import Union
import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.__support__ import json_dumps


def get_policy(conn:anylog_connector.AnyLogConnector, policy_type:str='*', where_condition:str=None,
               bring_case:str=None, bring_condition:str=None, seperator:str=None, destination:str=None,
               view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[list, str]:
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
        if return_cmd -> return command
        else -> return blockchain get result
    """
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
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def blockchain_sync(conn:anylog_connector.AnyLogConnector, ledger_conn:str, blockchain_source:str='master',
                    sync_time:str='30 seconds', blockchain_destination:str='file', destination:str=None,
                    view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[bool, str]:
    """
    Scheduled process for blockchain sync
    :args:
        conn:anylog_connector.AnyLogConnector - connection to
        ledger_conn:str - ledger connection information for master node use TCP IP:PORT
        blockchain_source:str - where the blockchain resides (default: master node)
        blockchain_destination:str - blockchain destination (default: file)
        destination:str - remote connection information
        view_help:bool - print help information
        return_cmd:bool - return command to be executed
        exception:bool - print exception
    :params:
        status
        headers:dict - REST header information
    :return:
        if return_cmd is True -> return command
        else ->
            True - success
            False - fail
    """
    headers = {
        "command": f"run blockchain sync where source={blockchain_source} and time={sync_time} and dest={blockchain_destination} and connection={ledger_conn}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd="POST", headers=headers, payload=None, exception=exception)

    return status


def execute_seed(conn:anylog_connector.AnyLogConnector, ledger_conn:str, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False)->Union[bool, str]:
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
        status - content returned
        headers:dict - REST header information
    :return:
        if return_cmd is True -> return command
        else ->
            True - success
            False - fail
    """
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
    else:
        status = execute_publish_cmd(conn=conn, cmd="POST", headers=headers, payload=None, exception=exception)

    return status


def prepare_policy(conn:anylog_connector.AnyLogConnector, policy:dict, destination:str=None, view_help:bool=False,
                   return_cmd:bool=False, exception:bool=False)->Union[bool, str]:
    """
    Prepare JSON policy - this also validates that the JSON policy is "OK"
    :args:
        conn:anylog_connector.AnyLogConnector - connection to
        policy:dict - policy to publish on blockchain
        destination:str - remote connection information
        view_help:bool - print help information
        return_cmd:bool - return command to be executed
        exception:bool - print exception
    :params:
        output - content returned
        headers:dict - REST header information
        new_policy:str - policy to prepare
    :return:
        if return_cmd is True -> return command
        else ->
            True - success
            False - fail
    """
    headers = {
        "command": "blockchain prepare policy !new_policy",
        "User-Agent": "AnyLog/1.23"
    }

    new_policy = f"<new_policy={policy}>"
    if isinstance(policy, dict):
        new_policy = f"<new_policy={json_dumps(content=policy, exception=exception)}>"

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd="POST", headers=headers, payload=new_policy, exception=exception)

    return status

def post_policy(conn:anylog_connector.AnyLogConnector, policy:dict, ledger_conn:str=None, blockchain_platform:str=None,
                destination:str=None, view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[bool, str]:
    """
    publish JSON policy
    :args:
        conn:anylog_connector.AnyLogConnector - connection to
        policy:dict - policy to publish on blockchain
        ledger_conn:str / blockchain_platform - which network the policy is stored on
        destination:str - remote connection information
        view_help:bool - print help information
        return_cmd:bool - return command to be executed
        exception:bool - print exception
    :params:
        status
        headers:dict - REST header information
        new_policy:str - policy to prepare-
    :return:
        if return_cmd is True -> return command
        else ->
            True - success
            False - fail
    """
    headers = {
        "command": f"blockchain insert where policy=!new_policy and local=true ",
        "User-Agent": "AnyLog/1.23"
    }
    if ledger_conn:
        headers['command'] += f'and master={ledger_conn}'
    elif blockchain_platform:
        headers['command'] += f'and blockchain={blockchain_platform}'

    new_policy = f"<new_policy={policy}>"
    if isinstance(policy, dict):
        new_policy = f"<new_policy={json_dumps(content=policy, exception=exception)}>"

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd="POST", headers=headers, payload=new_policy, exception=exception)

    return status


def config_from_policy(conn:anylog_connector.AnyLogConnector, policy_id:str, destination:str=None, view_help:bool=False,
                       return_cmd:bool=False, exception:bool=False):
    """
    Configure a node from the policy info
    :args:
        conn:anylog_connector.AnyLogConnector - connection to
        policy_id:str - policy ID to configure node based of off
        destination:str - remote connection information
        view_help:bool - print help information
        return_cmd:bool - return command to be executed
        exception:bool - print exception
    :params:
        status
        headers:dict - REST header information
    :return:
        if return_cmd is True -> return command
        else ->
            True - success
            False - fail
    """
    headers = {
        "command": f"config from policy where id={policy_id}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd="POST", headers=headers, payload=None, exception=exception)

    return status