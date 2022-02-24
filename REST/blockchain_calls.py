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


def declare_policy(anylog_conn:AnyLogConnection, policy_type:str, company_name:str, policy_values:str={},
                   master_node:str="!master_node", exception:bool=False)->bool:
    """
    Process to declare on blockchain
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        policy_type:str - policy type (ex. master, operator, cluster)
        company_name:str - name of company policy is correlated to
        policy_values:dict - values correlated to policy type
        master_node:str - master node to send policy to
        exception:bool - whether the command failed & why
    :params:
        status:bool
        policy:dict - policy to post on blockchain
        payload:str - policy converted to string
        headers:dict - REST header
    :return:
        status
    """
    status = True
    if 'company' not in policy_values:
        policy_values['company'] = company_name
    policy = {policy_type: policy_values}

    try:
        payload = f"<new_policy={json.dumps(policy)}>"
    except Exception as e:
        status = False
        if exception is True:
            print(f"Failed to convert {policy} to string (Error: {e})")

    if status is True: # blockchain prepare policy !new_policy
        headers = {
            "command": "blockchain prepare policy !new_policy",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.post(headers=headers, payload=payload)
        if r is False:
            status = False
            if exception is True:
                print(f"Failed to prepare '{payload}' (Error {e})")

    if status is True: # blockchain insert where policy=!new_policy and local=true and master=!master_node
        headers = {
            "command": "blockchain insert where policy=!new_policy and local=true and master=!master_node",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.post(headers=headers, payload=payload)
        if r is False:
            status = False
            if exception is True:
                print(f"Failed to insert '{payload}' (Error {e})")

    return status