# Blockchain Commands: https://github.com/AnyLog-co/documentation/blob/master/blockchain%20commands.md
from anylog_connector import AnyLogConnector
import rest_support

import generic_get_calls
import blockchain_support


def blockchain_sync(anylog_conn:AnyLogConnector, blockchain_source:str, blockchain_destination:str, sync_time:str,
                    ledger_conn:str, view_help:bool=False, exception:bool=False)->bool:
    """
    Enable automatic blockchain sync process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/blockchain%20configuration.md#synchronize-the-blockchain-data-with-a-local-copy-every-30-seconds
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
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True and r is False:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def get_policy(anylog_conn:AnyLogConnector, policy_type:str, where_conditions:dict=None, bring_conditions:str=None,
               bring_values:str=None, separator:str=None, view_help:bool=False, exception:bool=False)->str:
    """
    Execute `blockchain get` command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/blockchain%20commands.md#query-policies
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
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
        'command': blockchain_support.generate_blockchain_get(policy_type=policy_type,
                                                              where_conditions=where_conditions,
                                                              bring_conditions=bring_conditions,
                                                              bring_values=bring_values,
                                                              separator=separator),
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        r, error = anylog_conn.get(headers=headers)
        if r is False:
            if exception is True:
                rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            policies = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    return policies


def prepare_policy(anylog_conn:AnyLogConnector, policy:str, view_help:bool=False, exception:bool=False)->bool:
    """
    Prepare a policy for deploying on blockchain
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
    payload = f'<new_policy={policy}>'


    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        r, error = anylog_conn.post(headers=headers, payload=payload)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            status = True

    return status


def post_policy(anylog_conn:AnyLogConnector, policy:str=None, local_publish:bool=True, platform:str=None,
              ledger_conn:str=None, view_help:bool=False,  exception:bool=False)->bool:
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
        'command': 'blockchain insert where policy=!new_policy',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        headers=blockchain_support.generate_blockchain_insert(local_publish=local_publish, platform=platform,
                                                              ledger_conn=ledger_conn)

        if policy is not None:
            payload = f'<new_policy={policy}>'
            r, error = anylog_conn.post(headers=headers, payload=payload)
        else:
            r, error = anylog_conn.post(headers=headers)

        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def blockchain_synchronizer(anylog_conn:AnyLogConnector, ledger_conn:str, source:str='master', dest:str='file',
                            time:str='30 seconds', view_help:bool=False, exception:bool=False)->bool:
    """
    Declare blockchain synchronizer
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#blockchain-synchronizer
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        ledger_conn:str - The connection information that is needed to retrieve the data. For a Master, the IP and Port of the master node.
        source:str - The source of the metadata (blockchain or a Master Node).
        dest:str - The destination of the blockchain data such as a file (a local file) or a DBMS (a local DBMS).
        time:str - The frequency of updates.
        view_help:bool - whether to print information regarding command
        exception:bool - whether to print error messages
    :params:
        status:bool
        headers:dict - REST header information
    :return:
        True - success
        False - fails
        None - printed help information
    """
    status = None
    headers = {
        'command': f'run blockchain sync where source={source} and dest={dest} and time={time} and connection={ledger_conn}',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        r, error = anylog_conn.post(headers=headers, payload=None)
        if not isinstance(r, bool):
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status