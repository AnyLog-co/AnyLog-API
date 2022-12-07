from anylog_connection import AnyLogConnection
import generic_get_calls
import support

def blockchain_sync(anylog_conn:AnyLogConnection, blockchain_source:str, blockchain_destination:str, sync_time:str,
                    ledger_conn:str, exception:bool=False)->bool:
    """
    Enable automatic blockchain sync process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/blockchain%20configuration.md#synchronize-the-blockchain-data-with-a-local-copy-every-30-seconds
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        blockchain_source:str - source where data is coming from (default: master node)
        blockchain_destination:str - destination where data will be stored locally (default: file)
        sync_time:str - how often to sync
        ledger_conn:str - connection to blockchain ledger (for master use IP:Port)
        exception:bool - Whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status = True
    headers = {
        "command": f"run blockchain sync where source={blockchain_source} and time={sync_time} and dest={blockchain_destination} and connection={ledger_conn}",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True and r is False:
            support.print_rest_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def get_policy(anylog_conn:AnyLogConnection, policy_type:str, name:str, company:str=None, local_ip:str=None,
               anylog_server_port:int=None, member_type:str=None, exception:bool=False)->dict:
    """
    check whether policy exists, if exists then returns policy else returns empty dict
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        policy_type:str - policy type
        name:str - policy name
        company:str - Company which owns this policy
        local_ip:str - local IP
        anylog_server_port:int - AnyLog TCP port
        exception:bool - Whether to print exceptions
        member_type:str - member type for permissions and authentication
    :params:
        policy:dict - policy to return
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        if success returns policy, else returns {}
    """
    if len(company.split(' ')) > 1:
        company = f'"{company}"'
    headers = {
        'command': f"blockchain get {policy_type} where name={name}",
        "User-Agent": "AnyLog/1.23"
    }
    if company is not None:
        headers['command'] += f" and company={company}"
    if local_ip is not None:
        headers["command"] += f" and local_ip={local_ip}"
    if anylog_server_port is not None:
        headers["command"] += f" and port={anylog_server_port}"
    if member_type is not None:
        headers['command'] += f' and type={member_type}'
    if policy_type == "cluster":
        headers['command'] += " bring.first"

    r, error = anylog_conn.get(headers=headers)
    if r is False:
        policy = {}
        if exception is True:
            support.print_rest_error(error_type='GET', cmd=headers['command'], error=error)
    else:
        try:
            policy = r.json()[0]
        except:
            policy = {}

    return policy


def prepare_policy(anylog_conn:AnyLogConnection, policy:str, exception:bool=False)->str:
    """
    Prepare a policy for deploying on blockchain
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        policy:str - policy to store on blockchain
        exception:bool - Whether to print exceptions
    :params:
        output:str - "validation" that policy is ready to be deployed
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
        payload:str  - deceleration of policy
        anylog_configs:dict - AnyLog dictionary
    :return:
        if 'new_policy' in AnyLog dictionary then return it, else ""
    """
    headers = {
        'command': 'blockchain prepare policy !new_policy',
        'User-Agent': 'AnyLog/1.23'
    }
    payload = f'<new_policy={policy}>'
    r, error = anylog_conn.post(headers=headers, payload=payload)
    if r is False:
        output = {}
        if exception is True and r is False:
            support.print_rest_error(error_type='POST', cmd=headers['command'], error=error)
    else:
        anylog_configs = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, exception=exception)
        if 'new_policy' in anylog_configs:
            output = anylog_configs['new_policy']

    return output


def post_policy(anylog_conn:AnyLogConnection, policy:str, exception:bool=False)->bool:
    """
    POST policy to blockchain
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        policy:str - policy to store on blockchain
        exception:bool - Whether to print exceptions
    :params:
        output:str - "validation" that policy is ready to be deployed
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
        payload:str  - deceleration of policy
        anylog_configs:dict - AnyLog dictionary
    :return:
        True - if success
        False - if fails
    """
    status = True
    headers = {
        'command': 'blockchain insert where policy=!new_policy and local=true and master=!ledger_conn',
        'User-Agent': 'AnyLog/1.23'
    }

    payload = f'<new_policy={policy}>'

    r, error = anylog_conn.post(headers=headers, payload=payload)
    if r is False:
        status = False
        if exception is True and r is False:
            support.print_rest_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def post_signed_policy(anylog_conn:AnyLogConnection, policy_name:str='signed_policy', exception:bool=False)->bool:
    """
    POST policy to blockchain
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        policy_name:str - name of policy to POST
        exception:bool - Whether to print exceptions
    :params:
        output:str - "validation" that policy is ready to be deployed
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
        payload:str  - deceleration of policy
        anylog_configs:dict - AnyLog dictionary
    :return:
        True - if success
        False - if fails
    """
    status = True
    headers = {
        'command': 'blockchain insert where policy=!signed_policy and local=true and master=!ledger_conn',
        'User-Agent': 'AnyLog/1.23'
    }

    r, error = anylog_conn.post(headers=headers, payload=None)
    if r is False:
        status = False
        if exception is True and r is False:
            support.print_rest_error(error_type='POST', cmd=headers['command'], error=error)

    return status