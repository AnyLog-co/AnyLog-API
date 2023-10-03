# Blockchain Commands: https://github.com/AnyLog-co/documentation/blob/master/blockchain%20commands.md
from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.generic_get_calls import help_command
from anylog_api_py.blockchain_support import generate_blockchain_get
from anylog_api_py.rest_support import print_rest_error, extract_results
from anylog_api_py.__support__ import json_dumps

def blockchain_sync(anylog_conn:AnyLogConnector, blockchain_source:str, blockchain_destination:str, sync_time:str,
                    ledger_conn:str, view_help:bool=False, exception:bool=False)->bool:
    """
    Enable automatic blockchain sync process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#blockchain-synchronizer
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        blockchain_source:str - source where data is coming from (default: master node)
        blockchain_destination:str - destination where data will be stored locally (default: file)
        sync_time:str - how often to sync
        ledger_conn:str - connection to blockchain ledger (for master use IP:Port)
        view_help:bool - view help for function
        exception:bool - Whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        if help - return None
        if succeed - return True
        if fails - return False
    """
    status = None
    headers = {
        "command": f"run blockchain sync where source={blockchain_source} and time={sync_time} and dest={blockchain_destination} and connection={ledger_conn}",
        "User-Agent": "AnyLog/1.23"
    }
    if view_help is True:
        help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True and r is False:
                print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def get_policy(anylog_conn:AnyLogConnector, blockchain_get_cmd:str=None, policy_type:str=None, where_conditions:dict=None,
               bring_conditions:str=None, bring_values:str=None, separator:str=None, view_help:bool=False,
               exception:bool=False)->str:
    """
    Execute `blockchain get` command
        if user inputs a blockchain_stmt value then that'll be used for the command, otherwise command will be built
        using generate_blockchain_get
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/blockchain%20commands.md#query-policies
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        blockchain_get_cmd:str - complete `blockchain get` statement
        policy_type:str - policy types to get
        where_conditions:dict - dictionary of WHERE conditions (ex. {'company': 'New Company', 'rest_port': 32049})
        bring_conditions:str - bring conditions (ex. table, table.unique)
        bring_values:str - values to bring (ex. [*][ip]:[*][port])
        separator:str - how to separate values (if using new-line then \\n)
        view_help:bool - view help for function
        exception:bool - Whether to print exceptions
    :params:
        policies:dict - results from request
        headers:dict - REST dictionary
    :return:
        policies, if view_help then returns empty dict
    """
    policies = {}
    headers = {
        'command': blockchain_get_cmd,
        'User-Agent': 'AnyLog/1.23'
    }
    if headers['command'] is None and policy_type is None:
        if exception is True:
            print(f"Missing policy type...")
        return policies
    elif headers['command'] is None:
        headers['command'] = generate_blockchain_get(policy_type=policy_type, where_conditions=where_conditions,
                                                     bring_conditions=bring_conditions, bring_values=bring_values,
                                                     separator=separator)
    if view_help is True:
        help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        r, error = anylog_conn.get(headers=headers)
        if r is False:
            if exception is True:
                print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            policies = extract_results(cmd=headers['command'], r=r, exception=exception)

    return policies


def prepare_policy(anylog_conn:AnyLogConnector, policy:dict, view_help:bool=False, exception:bool=False)->bool:
    """
    Prepare a policy for deploying on blockchain
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/blockchain%20commands.md
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        policy:str - policy to store on blockchain
        view_help:bool - whether to print help for command
        exception:bool - Whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header
        payload:str - policy as a REST data payload for POST
        r:requests.post, error:str - result from REST POST command
    :return:
        if view_help is True - returns None
        if POST request succeeds - returns True
        if POST request fails - returns False
    """
    status = None
    headers = {
        'command': 'blockchain prepare policy !new_policy',
        'User-Agent': 'AnyLog/1.23'
    }
    if isinstance(policy, str):
        payload = f'<new_policy={policy}>'
    else:
        payload = f"<new_policy={json_dumps(policy)}>"

    if view_help is True:
        help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        r, error = anylog_conn.post(headers=headers, payload=payload)
        if r is False:
            status = False
            if exception is True:
                print_rest_error(call_type='POST', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            status = True

    return status


def post_policy(anylog_conn:AnyLogConnector, policy=None, ledger_conn:str=None, view_help:bool=False,
                exception:bool=False)->bool:
    """
    Post policy to blockchain
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/blockchain%20commands.md#the-blockchain-insert-command
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        policy:str - policy to publish (if not set code assumes policy is stored as !new_policy variable)
        local_publish:bool - A true/false value to determine an update to the local copy of the ledger
        platform:str - connected blockchain platform
        ledger_conn:str - The IP and Port value of a master node
    :params:
        status:bool
        headers:dict - headers for REST request
    """
    status = None
    headers = {
        'command': f'blockchain insert where policy=!new_policy and local=true',
        'User-Agent': 'AnyLog/1.23'
    }
    if ledger_conn is not None:
        headers['command'] += f" and master={ledger_conn}"
    if view_help is True:
        help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        if policy is not None:
            if isinstance(policy, str):
                payload = f'<new_policy={policy}>'
            else:
                payload = f"<new_policy={json_dumps(policy)}>"
            r, error = anylog_conn.post(headers=headers, payload=payload)
        else:
            r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True:
                print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status
