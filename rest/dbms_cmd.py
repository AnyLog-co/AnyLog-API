import __init__
import rest.anylog_api as anylog_api
import rest.blockchain_cmd as blockchain_cmd

import support.errors as errors

def get_dbms(conn:anylog_api.AnyLogConnect, exception:bool=False)->str: 
    """"
    Get list of connected databases 
    :args: 
        conn:anylog_api.AnyLogConnect - REST AnyLog Connection
        exception:bool - whether or not to print exception
    :params: 
        cmd:str - command to execute 
    :return:
    """
    output = None
    cmd = "get databases" 
    r, error = conn.get(command=cmd, query=False)

    if errors.get_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception) == False: 
        try: 
            output = r.text
        except Exception as e:
            if exception == True: 
                print('Failed to extract data from GET (Error: %s)' % e)
    return output

def connect_dbms(conn:anylog_api.AnyLogConnect, config:dict, db_name:str=None, exception:bool=False)->bool:
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
    if db_name == None and 'default_dbms' in config: 
        db_name = config['default_dbms']
    elif db_name == None and 'default_dbms' not in config: 
        if exception == True: 
            print('Missing database name') 
        status = False
       
    if status != False: 
        if 'db_type' not in config: 
            config['db_type'] = 'sqlite'
        if 'db_user' not in config: 
            config['db_user'] = 'anylog@127.0.0.1:anylog' 
        if 'db_port' not in config: 
            config['db_port'] = 5432

        cmd = "connect dbms %s %s %s %s" % (config['db_type'],  config['db_user'], config['db_port'], db_name)
        r, error = conn.post(command=cmd)
        status = errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception)
        if status == False: 
            status = True

    return status 

def check_table(conn:anylog_api.AnyLogConnect, db_name:str, table_name:str, exception:bool=False)->bool: 
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
    
    r, error = conn.get(command=cmd, query=False) 
    if errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception) == False:  
        try: 
            if r.json()['local'] == 'true':
                status = True 
        except: 
            if 'true' in r.text: 
                status = True
    return status 

def create_table(conn:anylog_api.AnyLogConnect, db_name:str, table_name:str, exception:bool=False)->bool: 
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
    if {db_name: table_name} in [{'blockchain': 'ledger'}, {'almgm': 'tsd_info'}] or blockchain_cmd.check_table(conn=conn, db_name=db_name, table_name=table_name, exception=exception) == True:  
        cmd = "create table %s where dbms=%s" % (table_name, db_name)
        r, error = conn.post(command=cmd)
        if errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception) == True: 
            status = False 
    else: 
        status = False 

    return status 
