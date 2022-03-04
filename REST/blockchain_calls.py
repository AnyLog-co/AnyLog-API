"""
URL: https://github.com/AnyLog-co/documentation/blob/master/blockchain%20commands.md
"""
import json
from anylog_connection import AnyLogConnection


def blockchain_get(anylog_conn:str, policy_type:str='*', where_condition:str=None, bring_param:str=None,
                   bring_condition:str=None, separator:str=None, exception:bool=False)->dict:
    """
    Execute blockchain get based on params
    :command:
        blockchain get operator where company=AnyLog  bring [operator][name] separator=,
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        policy_type:str - policy type to get from blockchain
        where_condition:str - where conditions
        bring_param:str - param correlated to bring command (ex. first)
        bring_condition:str - bring conditions
        separator:str - character to separate results by
    :params:
        blockchain_data:dict - Results from blockchain
        cmd:str - command to execute
        headers:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        blockchain_data
    """
    blockchain_data = None

    cmd = f"blockchain get {policy_type}"
    if where_condition is not None:
        cmd += f" where {where_condition}"
    if bring_condition is not None and bring_param is not None:
        cmd += f" bring.{bring_param} {bring_condition}"
    elif bring_condition is not None:
        cmd += f" bring {bring_condition}"
    if separator is not None:
        cmd += f" separator={separator}"

    headers = {
        "command": cmd,
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(error_type="GET", cmd=headers['command'], error=error)
    else:
        try:
            blockchain_data = r.json()
        except Exception as e:
            try:
                blockchain_data = r.text
            except Exception as e:
                if exception is True:
                    print(f"Failed to execute command {cmd} (Error: {e})")
    return blockchain_data


def declare_policy(anylog_conn:AnyLogConnection, policy:str, master_node:str="!master_node", exception:bool=False)->bool:
    """
    Process to declare policy in (blockchain) ledger
    :steps:
        1. prepare policy - Adds an ID and a date attributes to an existing policy.
        2. insert policy - Add a new policy to the ledger in one or more blockchain platform.s
    :commands:
        blockchain prepare policy !new_policy
        blockchain insert where policy=!new_policy and local=true and master=!master_node
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        policy:str - policy to store in blockchain
        master_node:str - master node to send policy to
        exception:bool - whether the command failed & why
    :params:
        status:bool
        policy:dict - policy to post on blockchain
        payload:str - policy converted to string
        headers:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status = True

    payload = f"<new_policy={policy}>"
    if isinstance(policy, dict):
        try: # convert policy to AnyLog JSON policy object
            payload = f"<new_policy={json.dumps(policy)}>"
        except Exception as e:
            pass

    if status is True: # prepare policy
        headers = {
            "command": "blockchain prepare policy !new_policy",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.post(headers=headers, payload=payload)
        if r is False:
            status = False
            if exception is True:
                print(f"Failed to prepare '{payload}' (Error {e})")

    if status is True: # insert policy
        headers = {
            "command": f"blockchain insert where policy=!new_policy and local=true and master={master_node}",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.post(headers=headers, payload=payload)
        if r is False:
            status = False
            if exception is True:
                print(f"Failed to insert '{payload}' (Error {e})")

    return status


def drop_policy(anylog_conn:AnyLogConnection, policy:dict, exception:bool=False)->bool:
    """
    Execute drop policy
    :command:
        blockchain drop policy !drop_policy
    :ars:
        anylog_conn:AnyLogConnection - connection to AnyLog
        policy:dict - policy to drop
        exception:bool - whether the command failed & why
    :params:
        payload:str - drop policy payload
        headers:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    if isinstance(policy, dict):
        policy = json.dump(policy)

    payload = f"<drop_policy={policy}>"

    headers = {
        "command": "blockchain drop policy !drop_policy",
        "User-Agent": "AnyLog/1.23"
    }

    r, error = anylog_conn.post(headers=headers, payload=payload)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)