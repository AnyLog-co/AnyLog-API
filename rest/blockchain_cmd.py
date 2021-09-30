import json

import __init__
import anylog_api
import get_cmd
import errors


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

    blockchain = []
    r, error = conn.get(command=cmd)
    if not errors.get_error(conn.conn, command=cmd, r=r, error=error, exception=exception):
        try: 
            blockchain = r.json()
        except:
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
    cmd = "get table blockchain status where dbms = %s and name = %s" % (db_name, table_name)
    
    r, error = anylog_api.get(command=cmd, query=False)
    if not errors.get_error(conn.conn, command=cmd, r=r, error=error, exception=exception):
        try: 
            if r.json()['local'] == 'true':
                status = True 
        except Exception:
            if 'true' in r.text: 
                status = True

    return status 


def pull_json(conn:anylog_api.AnyLogConnect, master_node:str='local', exception:bool=False)->bool: 
    """
    pull json from blockchain
    :args: 
        conn:str - REST connection info
        master_node:str - master node
        auth:tuple - Authentication information
        timeout:int - REST timeout
    :param: 
        cmd:str - command to execute 
        status:bool
    :return:
        status
    """
    status = True
    cmd = "blockchain pull to json !blockchain_file"
    if master_node == 'local':
        r, error = conn.post(command=cmd)
    else:
        r, error = conn.post(command=cmd, remote_node=master_node)

    if not errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception):
        if master_node != 'local':
            cmd = 'file get !!blockchain_file !blockchain_file'
            r, error = conn.post(command=cmd, remote_node=master_node)
            if not errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception):
                status = True
    else: 
        status = False 

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
    if isinstance(policy, dict): # convert policy to str if dict
        policy = json.dumps(policy)
    raw_data="<policy=%s>" % policy 

    r, error = conn.post_policy(policy=raw_data, master_node=master_node)
    status = errors.post_error(conn=conn.conn, command='blockchain post policy %s' % raw_data, r=r, error=error, exception=exception)
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
    if isinstance(policy, dict): # convert policy to str if dict
        policy = json.dumps(policy)
    raw_data="<policy=%s>" % policy 

    r, error = conn.drop_policy(policy=raw_data, master_node=master_node)
    if errors.post_error(conn=conn.conn, command='blockchain drop policy policy %s' % raw_data, r=r, error=error, exception=exception):
        status = False

    return status


def blockchain_sync(conn:anylog_api.AnyLogConnect, source:str, time:str, connection:str=None, exception:bool=False)->bool: 
    """
    Set Blockchain sync 
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        source:str - source to sync from 
            --> master 
            --> dbms 
        time:str - how often data is synced
        connection:str - for master source, the corresponding IP:PORT 
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
    if source == 'master' and connection is None:
        if exception is True:
            print('When source is set to master, connection must be set')
        status = False 

    if 'Not declared' in get_cmd.get_processes(conn=conn, exception=exception).split('Blockchain Sync')[-1].split('\r')[0] and status is True:
        cmd = 'run blockchain sync where source=%s and time=%s and dest=file' % (source, time) 
        if source == 'master': 
            cmd += " and connection=%s" % connection

        r, error = conn.post(command=cmd)
        if errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception):
            status = False

    return status 
