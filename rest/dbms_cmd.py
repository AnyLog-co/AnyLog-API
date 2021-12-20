import import_packages
import_packages.import_dirs()

import anylog_api
import blockchain_cmd
import other_cmd

HEADER = {
    "command": None,
    "User-Agent": "AnyLog/1.23"
}


def get_dbms(conn:anylog_api.AnyLogConnect, exception:bool=False)->list:
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
    database_list = []
    HEADER['command'] = "get databases"
    r, error = conn.get(headers=HEADER)

    if not other_cmd.print_error(conn=conn.conn, request_type="get", command=HEADER['command'], r=r, error=error,
                            exception=exception):
        try:
            output = r.text
        except Exception as e:
            if exception is True:
                print('Failed to extract data from GET (Error: %s)' % e)

    if output == 'No DBMS connections found':
        database_list = output
    else:
        for db in output.split('\n'):
            if 'sqlite' in db or 'psql' in db:
                database_list.append(db.split(' ')[0].rstrip().lstrip())

    return database_list


def get_dbms_type(conn:anylog_api.AnyLogConnect, exception:bool=False)->dict:
    """"
    Get list of connected databases with their database type
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
    datbase_list = {}
    HEADER['command'] = "get databases"
    r, error = conn.get(headers=HEADER)

    if not other_cmd.print_error(conn=conn.conn, request_type="get", command=HEADER['command'], r=r, error=error,
                            exception=exception):
        try:
            output = r.text
        except Exception as e:
            if exception is True:
                print('Failed to extract data from GET (Error: %s)' % e)

    if output == 'No DBMS connections found':
        datbase_list = output
    else:
        for db in output.split('\n'):
            if 'sqlite' in db or 'psql' in db:
                db = ' '.join(db.split())
                # print(db.split(' ')[0].rstrip().lstrip(), db.split(' ')[1].rstrip().lstrip())
                datbase_list[db.split(' ')[0]] = db.split(' ')[1]

    return datbase_list


def connect_dbms(conn:anylog_api.AnyLogConnect, db_type:str='sqlite', db_credentials:str=None, db_port:int=5432,
                 db_name:str=None, exception:bool=False)->bool:
    """
    Execute connection to database
    :args: 
        conn:str - REST connection info
        db_type:str - database type
        db_credentials:str - database user@ip:password
        db_port:str - database port
        db_name:str - database you'd like to create
    :param: 
        cmd:str - command to execute 
        status:bool
    :return:
        status
    """
    HEADER['command'] = "connect dbms %s %s %s %s" % (db_type, db_credentials, db_port, db_name)
    r, error = conn.post(headers=HEADER)
    if not other_cmd.print_error(conn=conn.conn, request_type="post", command=HEADER['command'], r=r, error=error, exception=exception):
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
    HEADER['command'] = 'disconnect dbms %s' % db_name

    r, error = conn.post(headers=HEADER)
    if other_cmd.print_error(conn=conn, request_type="pull", command=HEADER['command'], r=r, error=error, exception=exception):
        status = False

    if status is True: # validate database was disconnected
        dbms_list = get_dbms(conn=conn, exception=exception)
        if db_name in dbms_list:
            status = False

    return status


def drop_dbms(conn:anylog_api.AnyLogConnect, db_name:str, db_type:str, exception:bool=False)->bool:
    """
    Drop database
        :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        db_name:str - database to drop
        db_type:str - logical database type (ex. SQLite, Postgres)
        exception:bool - whether to print exceptions
    :params:
        status:bool
        HEADER:dict - REST request header info
    :return:
        status
    """
    status = True
    HEADER['command'] = 'drop dbms %s from %s' % (db_name, db_type)

    r, error = conn.post(headers=HEADER)
    if other_cmd.print_error(conn=conn, request_type="pull", command=HEADER['command'], r=r, error=error,
                                 exception=exception):
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


def drop_partitions(conn:anylog_api.AnyLogConnect, db_name:str, partition_name:str=None, table_name:str='*',
                    keep:int=30, scheduled:bool=False, exception:bool=False)->bool:
    """
    Process to drop partition(s)
    :options:
        1. drop a specific partition (partition_name), table_name should correlate to partiiton name (ie not '*')
        2. drop partitions for a database or table within database
        3. set option 3 as a scheduled process
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        db_name:str - database name
        partition_name:str - specific partition to drop (wont run as a scheduled process)
        table_name:str - table to drop partitions from
        keep:int - number of days to keep -- if set to 0 won't keep any
        scheduled:bool - if True set to a scheduled process once a day
        exception:bool - whether to print exceptions
    :params:
        status:bool
        cmd:str - command to execute
        HEADER:dict - REST header information
    :return:
        status
    """
    status = True
    if partition_name is not None:
        cmd = "drop partition %s where dbms=%s and table=%s" % (partition_name, db_name, table_name)
    elif keep < 1:
        cmd = "drop partition where dbms=%s and table=%s" % (db_name, table_name)
    else:
        cmd = "drop partition where dbms=%s and table=%s and keep=%s" % (db_name, table_name, keep)

    if partition_name is None and scheduled is True:
        schedule_cmd = "schedule     time=1 day and name='drop partitions' task %s"
        cmd = schedule_cmd % cmd

    HEADER['command']=cmd

    r, error = conn.post(headers=HEADER)
    if other_cmd.print_error(conn=conn.conn, request_type='post', command=cmd, r=r, error=error,
                                 exception=exception):
        status = False

    return status



