import rest 
import blockchain_cmd 

def connect_dbms(conn:str, config:dict, db_name:str, auth:tuple=None, timeout:int=30)->bool: 
    """
    Execute connection to database
    :args: 
        conn:str - REST connection info
        config:dict - dict to extract config from
        db_name:str - database you'd like to create
        auth:tuple - Authentication information
        timeout:int - REST timeout
    :param: 
        cmd:str - command to execute 
        status:bool
    """
    status = True
    if 'db_type' not in config: 
        config['db_type'] = 'sqlite'
    if 'db_user' not in config: 
        config['db_type'] = 'anylog@127.0.0.1:anylog' 
    if 'db_port' not in config: 
        config['db_port'] = 5432

    cmd = "connect dbms %s %s %s %" % (config['db_type'],  config['db_user'], config['db_port'], db_name)
    
    status = rest.post(conn=conn, command=cmd, auth=auth, timeout=timeout) 

    return status 

def check_table(conn:str, db_name:str, table_name:str, auth:tuple=None, timeout:int=30)->bool: 
    """
    Check if table exists locally 
    :args: 
        conn:str - REST connection info
        db_name:str - database you'd like to use
        table_name:str - table you'd like to ccheck
        auth:tuple - Authentication information
        timeout:int - REST timeout
    :param: 
        cmd:str - command to execute 
        status:bool
    """
    status = False 
    cmd = "get table local status where dbms = %s and name = %s" % (db_name, table_name)
    
    r, e = rest.get(conn=conn, command=cmd, auth=auth, timeout=timeout) 
    try: 
        if r.json()['local'] == 'true':
            status = True 
    except: 
        if 'true' in r.text: 
            status = True

    return status 


def create_table(conn:str, db_name:str, table_name:str, auth:tuple=None, timeout:int=30)->bool: 
    """
    Create table based on db & table names
    :args: 
        conn:str - REST connection info
        db_name:str - database you'd like to use
        table_name:str - table you'd like to ccheck
        auth:tuple - Authentication information
        timeout:int - REST timeout
    :param: 
        cmd:str - command to execute 
        status:bool
    """
    status = True
    # Check if table can be executed either hardcode or blockchain 
    if {db_name: table_name} not [{'blockchain': 'ledger'}, {'almgm': 'tsd_info'}]: 
        if not blockchain_cmd.check_table(conn=conn, db_name=db_name, table_name=table_name, auth=auth, timeout=timeout): 
            status = False

    if status == True: 
        cmd = "create table %s where dbms=%s" % (table_name, db_name)
        status = rest.post(conn=conn, command=cmd, auth=auth, timeout=timeout)

    return status 
