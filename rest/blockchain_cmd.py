import json

import __init__
import anylog_api
import get_cmd
import errors

HEADER = {
    "command": None,
    "User-Agent": "AnyLog/1.23"
}


def master_pull_json(conn:anylog_api.AnyLogConnect, master_node:str='local', exception:bool=False)->bool:
    """
    Blockchain pull to JSON from master node
    :args:
        conn:str - REST connection info
        master_node:str - master node
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
    if errors.print_error(conn=conn.conn, request_type='post', command='blockchain pull to json', r=r, error=error, exception=exception):
        status = False

    if 'destination' in HEADER:
        del HEADER['destination']
    return status


def blockchain_get(conn:anylog_api.AnyLogConnect, policy_type:str='*', where:list=[], exception:bool=False)->list:
    """
    blockchain GET command 
    :args: 
        conn:str - REST connection info
        policy_type:str - policy type to get (default: all) 
        where:list - where condition (ex. [ip='127.0.0.1', port=2048])
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
    cmd = "blockchain get %s" % policy_type
    if where is not []:
        cmd += " where" 
        for value in where:
           cmd += " " + value
           if value != where[-1]: 
               cmd += " and"
    HEADER['command'] = cmd
    blockchain = []

    r, error = conn.get(headers=HEADER)
    if not errors.print_error(conn.conn, request_type="get", command=cmd, r=r, error=error, exception=exception):
        try: 
            blockchain = r.json()
        except Exception as e:
            print(e, r.text)
            blockchain = r.text
            
    return blockchain 


def check_table(conn:str, db_name:str, table_name:str, exception:bool=False)->bool: 
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
    if not errors.print_error(conn.conn, request_type="get", command=cmd, r=r, error=error, exception=exception):
        try: 
            if r.json()['local'] == 'true':
                status = True 
        except Exception:
            if 'true' in r.text: 
                status = True

    return status


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
    if not errors.print_error(conn=conn.conn, request_type="post", command='blockchain post policy %s' % raw_policy,
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
    if errors.print_error(conn=conn.conn, request_type='post', command='blockchain drop policy %s' % raw_policy, r=r,
                            error=error, exception=exception):
        status = False

    return status


def blockchain_sync(conn:anylog_api.AnyLogConnect, source:str, time:str, master_node:str=None, exception:bool=False)->bool:
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
        print(cmd)
        HEADER['command'] = cmd
        r, error = conn.post(headers=HEADER)
        if errors.print_error(conn=conn.conn, request_type="post", command=cmd, r=r, error=error, exception=exception):
            status = False

    return status 
