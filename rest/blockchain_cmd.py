import json

import __init__
import anylog_api
import config
import get_cmd
import post_cmd
import other_cmd

HEADER = {
    "command": None,
    "User-Agent": "AnyLog/1.23"
}


def __build_blockchain_query(policy_type:str="*", where_conditions:list=None, policy:dict=None)->str:
    """
    Build blockchain GET command
    :args:
        policy_type:str - policy type
        where:list - where conditions
        policy:dict - policy to generate where condition (if where is [])
    :params:
        cmd:str - blockchain command
    :return:
        cmd
    """
    cmd = "blockchain get %s" % policy_type
    if where_conditions is None and policy is not None:
        where_conditions = []
        for key in policy:
            if key != 'id' and key != 'date':
                where_conditions.append(other_cmd.format_string(key, policy[policy_type][key]))

    if where_conditions is not None:
        cmd += " where"
        for value in where_conditions:
           cmd += " " + value
           if value != where_conditions[-1]:
               cmd += " and"

    return cmd


def blockchain_get(conn:anylog_api.AnyLogConnect, policy_type:str='*', where_conditions:list=[], exception:bool=False)->list:
    """
    blockchain GET command 
    :args: 
        conn:str - REST connection info
        policy_type:str - policy type to get (default: all) 
        where_conditions:list - where condition (ex. [ip='127.0.0.1', port=2048])
        bring:list - values to extract from blockchain
        separator:str - how to separate results 
        auth:tuple - Authentication information
        timeout:int - REST timeout
    :param: 
        cmd:str - command to execute 
        blockchain:list - data extracted
    :return:
        blockchains
    """
    cmd = __build_blockchain_query(policy_type=policy_type, where_conditions=where_conditions, policy=None)
    HEADER['command'] = cmd
    blockchain = []

    r, error = conn.get(headers=HEADER)
    if not other_cmd.print_error(conn.conn, request_type="get", command=cmd, r=r, error=error, exception=exception):
        try: 
            blockchain = r.json()
        except Exception as e:
            print(e, r.text)
            blockchain = r.text
            
    return blockchain 


def check_table(conn:anylog_api.AnyLogConnect, db_name:str, table_name:str, exception:bool=False)->bool:
    """
    Check if table exists in blockchain
    :args: 
        conn:str - REST connection info
        db_name:str - database you'd like to use
        table_name:str - table you'd like to ccheck
        auth:tuple - Authentication information
        timeout:int - REST timeout
    :param: 
        cmd:str - command to execute 
        status:bool
    :return:
        status
    """
    status = False 
    HEADER['command'] = "get table blockchain status where dbms = %s and name = %s" % (db_name, table_name)
    r, error = anylog_api.get(headers=HEADER)
    if not other_cmd.print_error(conn.conn, request_type="get", command=cmd, r=r, error=error, exception=exception):
        try: 
            if r.json()['local'] == 'true':
                status = True 
        except Exception:
            if 'true' in r.text: 
                status = True

    return status


def __extract_policy_id(conn:anylog_api.AnyLogConnect, policy_type:str, exception:bool=False)->str:
    """
    Extract new policy ID from dictionary following prepare command
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        policy_type:str - node type that's being processed
        exception:bool - whether to print exception
    :params:
        policy_id - ID of new policy
    :return:
        policy_id
    """
    policy_id = None
    config_data = config.import_config(conn=conn, exception=exception)
    if 'policy' in config_data:
        try:
            policy_id = json.loads(config_data['policy'])[policy_type]['id']
        except Exception as e:
            if exception is True:
                print('Failed to extract policy ID (Error: %s)' % e)

    return policy_id


def prepare_policy(conn:anylog_api.AnyLogConnect, policy_type:str, policy:dict, exception:bool=False):
    """
    Prepare policy to post in blockchain
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog,
        policy_type:str - policy type
        policy:dict - policy to prepare
        exception:bool - whether to print exceptions
    :params;
        status:bool
        policy_id:dict - policy ID based on prepared policy
    :return:
        prep_policy
    """
    policy_id = None

    HEADER['command'] = 'blockchain prepare policy !policy'
    if isinstance(policy, dict): # convert policy to str if dict
        policy = json.dumps(policy)
    raw_policy="<policy=%s>" % policy

    # prepare policy
    r, error = conn.post(headers=HEADER, payload=raw_policy)
    if not other_cmd.print_error(conn=conn.conn, request_type='post', command='blockchain prepare policy %s' % raw_policy,
                                 r=r, error=error, exception=exception):
        policy_id = __extract_policy_id(conn=conn, policy_type=policy_type, exception=exception)

    return policy_id


def post_policy(conn:anylog_api.AnyLogConnect, policy:dict, master_node:str, exception:bool=False)->bool: 
    """
    POST policy to blockchain
    :args: 
        conn:anylog_api.AnyLogConnect - Connection to AnyLog
        policy:dict - policy to POST 
        master_node:str - IP & Port of master node 
        exception:bool - whether or not to print error to screen
    :params: 
        status:bool 
        raw_data:str - raw data 
    :return: 
        status
    """
    status = True
    header = HEADER
    header['command'] = 'blockchain push !policy'
    header['destination'] = master_node

    if isinstance(policy, dict): # convert policy to str if dict
        policy = json.dumps(policy)
    raw_policy="<policy=%s>" % policy

    r, error = conn.post(headers=header, payload=raw_policy)
    if not other_cmd.print_error(conn=conn.conn, request_type="post", command='blockchain post policy %s' % raw_policy,
                              r=r, error=error, exception=exception):
        status = False

    if 'destination' in HEADER:
        del HEADER['destination']
    return status 


def drop_policy(conn:anylog_api.AnyLogConnect, policy:dict, master_node:str, exception:bool=False)->bool:
    """
    Drop policy from blockchain
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        policy:dict - policy to drop
        master_node:str - master IP & Port
        exception:bool
    :params:
        status:bool 
        raw_data:str - raw data 
    :return: 
        status
    """
    status = True
    header = HEADER
    header['command'] = 'blockchain drop policy !policy'
    header['destination'] = master_node

    if isinstance(policy, dict): # convert policy to str if dict
        policy = json.dumps(policy)
    raw_policy="<policy=%s>" % policy

    r, error = conn.post(headers=header, payload=raw_policy)
    if other_cmd.print_error(conn=conn.conn, request_type='post', command='blockchain drop policy %s' % raw_policy, r=r,
                            error=error, exception=exception):
        status = False

    return status


def master_pull_json(conn: anylog_api.AnyLogConnect, master_node: str = 'local', master_file: str = "!!blockchain_file",
                     local_file: str = "!blockchain_file", exception: bool = False) -> bool:
    """
    Blockchain pull to JSON from master node - an alternative process to 'run blockchain sync' when sync process
        is not running in the background.
    :args:
        conn:str - REST connection info
        master_node:str - master node
        master_file:str - path to blockchain file in master node
        local_file:str - path to blockchain file in local (conn.conn) node
        exception:bool - whether to print exceptions
    :param:
        status:bool
        header:dict - Header
    :return:
        status
    """
    status = True
    header = HEADER
    header['command'] = "blockchain pull to json !blockchain_file"
    if master_node != 'local':
        header['command'] = header['command'].replace('!blockchain_file', '!!blockchain_file')
        header['destination'] = master_node

    r, error = conn.post(headers=header)
    if other_cmd.print_error(conn=conn.conn, request_type='post', command='blockchain pull to json', r=r, error=error,
                             exception=exception):
        status = False

    # copy blockchain file from master node locally
    if master_node != 'local' and status is True:
        status = post_cmd.copy_file(conn=conn, remote_node=master_node, remote_file=master_file, local_file=local_file,
                                    exception=exception)

    if 'destination' in HEADER:
        del HEADER['destination']
    return status


def blockchain_sync_scheduler(conn:anylog_api.AnyLogConnect, source:str, time:str, master_node:str=None, exception:bool=False)->bool:
    """
    Set Blockchain sync 
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        source:str - source to sync from 
            --> master 
            --> dbms 
        time:str - how often data is synced
        master_node:str - for master source, the corresponding IP:PORT
        exception:bool - whether to print error to screen
    :params: 
        status:bool 
        cmd:str - command to execute
    :return: 
        status
    """
    status = True
    if source not in ['master', 'dbms']: 
        if exception is True:
            print('Invalid source: %s. Options: master, dbms' % source)
        status = False 
    if source == 'master' and master_node is None:
        if exception is True:
            print('When source is set to master, master_node must be set')
        status = False 

    if 'Not declared' in get_cmd.get_processes(conn=conn, exception=exception).split('Blockchain Sync')[-1].split('\r')[0] and status is True:
        cmd = 'run blockchain sync where source=%s and time=%s and dest=file' % (source, time)

        if source == 'master': 
            cmd += " and connection=%s" % master_node
        HEADER['command'] = cmd
        r, error = conn.post(headers=HEADER)
        if other_cmd.print_error(conn=conn.conn, request_type="post", command=cmd, r=r, error=error, exception=exception):
            status = False

    return status 


def blockchain_sync(conn:anylog_api.AnyLogConnect, exception:bool=False)->bool:
    """
    Execute "run blockchain sync" - blockchain sync scheduled process should alrady be running
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        exception:bool - whether to write exceptions
    :params:
        status:bool
        HEADER - HEADER REST info
    :return:
        status
    """
    status = True
    HEADER['command'] = "run blockchain sync"
    r, error = conn.post(headers=HEADER)
    if other_cmd.print_error(conn=conn.conn, request_type="post", command=HEADER['command'], r=r, error=error,
                             exception=exception):
        status = False
    return status


def blockchain_wait(conn:anylog_api.AnyLogConnect, policy_type:str, where_conditions:list=[], exception:bool=False)->bool:
    """
    Execute blockchain wait process
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        policy_type:str - policy type
        policy:dict - policy that was executed
        exception:bool - whether to print exception
    :params:
        status:bool
        cmd:str - blockchain get command
        wait_cmd:str - wait command
    :return:
        status
    """
    status = True
    cmd = __build_blockchain_query(policy_type=policy_type, where_conditions=where_conditions)
    print(cmd)
    wait_cmd = "blockchain wait where command='%s'" % cmd
    HEADER['command'] = wait_cmd

    r, error = conn.post(headers=HEADER['command'])
    if other_cmd.print_error(conn=conn.conn, request_type='post', command=wait_cmd, r=r, error=error,
                             exception=exception):
        status = False

    return status
