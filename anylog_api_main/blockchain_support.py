import support


def generate_blockchain_get(policy_type:str, where_conditions:dict=None, bring_conditions:str=None,
                            bring_values:str=None, separator:str=None)->str:
    """
    Generate `blockchain get` command based on params
    :args:
        policy_type:str - policy types to get
        where_conditions:dict - dictionary of WHERE conditions (ex. {"company": "New Company", "rest_port": 32049})
        bring_conditions:str - bring conditions (ex. table, table.unique)
        bring_values:str - values to bring (ex. [*][ip]:[*][port])
        separator:str - how to separate values (if using new-line then \\n)
    :params:
        command:str - generated blockchain get command
        policy_type:list - converted policy_type to list of policy types
        where_stmt:str - built where condition based on where_conditions
        bring_stmt:str - built bring conditions
    :return:
        command
    """
    command = "blockchain get ("
    policy_type = policy_type.strip().split(",")
    for policy in policy_type:
        command += policy.strip()
        if policy != policy_type[-1]:
            command += ", "
        else:
            command += ")"

    if where_conditions is not None:
        where_stmt = "where"
        for key in where_conditions:
            if isinstance(where_conditions[key], str) and " " in where_conditions[key]:
                where_stmt += f' {key}="{where_conditions[key]}"'
            else:
                where_stmt += f" {key}={where_conditions[key]}"
            if key != list(where_conditions.keys())[-1]:
                where_stmt += " and"
        command += " " + where_stmt

    if bring_conditions is not None or bring_values is not None:
        bring_stmt = "bring"
        if bring_conditions is not None:
            bring_stmt += f".{bring_conditions}"
        if bring_values is not None:
            bring_stmt += f" {bring_values}"
        command += " " + bring_stmt

    if separator is not None:
        command += f" separator={separator}"

    return command


def generate_blockchain_insert(local_publish:bool=True, platform:str=None, ledger_conn:str=None)->str:
    """
    Generate blockchain insert statement
    :sample command:
        blockchain insert where policy = !policy and local = true and master = !master_node
        blockchain insert where policy = !policy and local = true and blockchain = ethereum
    :args:
        local_publish:bool - A true/false value to determine an update to the local copy of the ledger
        platform:str - connected blockchain platform
        ledger_conn:str - The IP and Port value of a master node
    :params:
        command:str - generated blockchain insert command
    :return:
        command
    """
    command = 'blockchain insert where policy=!new_policy'
    if local_publish is False:
        command += " and local=false"
    else:
        command += " and local=true"

    if platform in ['ethereum', 'eos', 'jasmy']:
        command += f" and blockchain={platform}"

    if ledger_conn is not None:
        command += f' and master={ledger_conn}'

    return command



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


