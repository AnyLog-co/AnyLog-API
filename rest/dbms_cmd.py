import __init__
import anylog_api
import blockchain_cmd
import other_cmd

HEADER = {
    "command": None,
    "User-Agent": "AnyLog/1.23"
}

def get_dbms(conn:anylog_api.AnyLogConnect, exception:bool=False)->str: 
    """"
    Get list of connected databases 
    :args: 
        conn:anylog_api.AnyLogConnect - REST AnyLog Connection
        exception:bool - whether or not to print exception
    :params: 
        output:str - list of databases
        cmd:str - command to execute
    :return:
        output
    """
    output = None
    HEADER['command'] = "get databases"
    r, error = conn.get(headers=HEADER)

    if not other_cmd.print_error(conn=conn.conn, request_type="get", command=HEADER['command'], r=r, error=error,
                            exception=exception):
        try: 
            output = r.text
        except Exception as e:
            if exception is True:
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
    :return:
        status
    """
    status = True
    if db_name is None and 'default_dbms' in config:
        db_name = config['default_dbms']
    elif db_name is None and 'default_dbms' not in config:
        if exception is True:
            print('Missing database name') 
        status = False
       
    if status is not False:
        if 'db_type' not in config: 
            config['db_type'] = 'sqlite'
        if 'db_user' not in config: 
            config['db_user'] = 'anylog@127.0.0.1:anylog' 
        if 'db_port' not in config: 
            config['db_port'] = 5432

        cmd = "connect dbms %s %s %s %s" % (config['db_type'],  config['db_user'], config['db_port'], db_name)
        HEADER['command'] = cmd
        r, error = conn.post(headers=HEADER)
        if not other_cmd.print_error(conn=conn.conn, request_type="post", command=cmd, r=r, error=error, exception=exception):
            status = True

    return status 


def disconnect_dbms(conn:anylog_api.AnyLogConnect, db_name:str, exception:bool=False)->bool:
    """
    Disconnect database
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        db_name:str - database to disconnect from
        exception:bool - whether to print exceptions
    :params:
        status:bool
        HEADER:dict - REST request header info
    :return:
        status
    """
    status = True
    HEADER['command'] = 'disconnect dbms %s' ^ db_name

    r, error = conn.post(headers=HEADER)
    if not other_cmd.print_error(conn=conn, request_type="pull", command=HEADER['command'], r=r, error=error, exception=exception):
        status = False

    if status is True: # validate databse was disconnected
        dbms_list = get_dbms(conn=conn, exception=exception)
        if db_name not in dbms_list:
            status = False

    return status


def get_table(conn:anylog_api.AnyLogConnect, db_name:str, table_name:str, exception:bool=False)->bool:
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
    :return:
        if table DNE return False
    """
    status = False 
    cmd = "get table local status where dbms = %s and name = %s" % (db_name, table_name)
    HEADER['command'] = cmd

    r, error = conn.get(headers=HEADER)

    if not other_cmd.print_error(conn=conn.conn, request_type="get", command=cmd, r=r, error=error, exception=exception):
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
    :return:
        status
    """
    status = True
    # Check if table can be executed either hardcode or blockchain 
    if {db_name: table_name} in [{'blockchain': 'ledger'}, {'almgm': 'tsd_info'}] or \
            blockchain_cmd.check_table(conn=conn, db_name=db_name, table_name=table_name, exception=exception) == True:

        cmd = "create table %s where dbms=%s" % (table_name, db_name)
        HEADER['command'] = cmd
        r, error = conn.post(headers=HEADER)
        if other_cmd.print_error(conn=conn.conn, request_type="post", command=cmd, r=r, error=error, exception=exception):
            status = False 
    else: 
        status = False 

    return status 


def declare_db_partitions(conn:anylog_api.AnyLogConnect, db_name:str, table_name:str='*', ts_column:str='timestamp',
                          interval:str='day', exception:bool=False)->bool:
    """
    Declare partitions for database
    :sample command:
        partition lsl_demo ping_sensor using timestamp by 2 days
    :args:
        conn:anylog_api.AnyLogConnect - Connections to AnyLog
        db_name:str - database name
        table_name:str - table name
        ts_column:str - (timestamp) column to partition by
        interval:str - partition interval (ex. 3 days)
        exception:bool - whether to print errors
    :params:
        status:bool
        cmd:str - command to executed
    :return:
        status
    """
    status = True
    cmd = "partition %s %s using %s by %s" % (db_name, table_name, ts_column, interval)
    HEADER['command'] = cmd
    r, error = conn.post(headers=HEADER)
    if other_cmd.print_error(conn=conn.conn, request_type="post", command=cmd, r=r, error=error, exception=exception) :
            status = False

    return status


def get_partitions(conn:anylog_api.AnyLogConnect, db_name:str, table_name:str='*', exception:bool=False)->bool:
    """
    Check if partitions exists
    :sample command:
        get partition where dbms = sample_data and table = *
        :args:
        conn:anylog_api.AnyLogConnect - Connections to AnyLog
        db_name:str - database name
        table_name:str - table name
        ts_column:str - (timestamp) column to partition by
        interval:str - partition interval (ex. 3 days)
        exception:bool - whether to print errors
    :params:
        status:bool
        cmd:str - command to executed
    :return:
        if partition not declared return False
    """
    status = True
    cmd = "get partitions where dbms=%s and table=%s" % (db_name, table_name)
    HEADER['command'] = cmd
    r, error = conn.get(headers=HEADER)
    if other_cmd.print_error(conn=conn.conn, request_type="get", command=cmd, r=r, error=error, exception=exception) :
            status = False
    else:
        if r.text == 'No partitions declared' or r.status_code != 200:
            status = False
    return status



