"""
URL: https://github.com/AnyLog-co/documentation/blob/master/sql%20setup.md
"""
from anylog_connection import AnyLogConnection
from support import print_error


def get_dbms(anylog_conn:AnyLogConnection, exception:bool=False)->list:
    """
    Get list of database connected locally
    :command:
        get databases
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        db_list:list - list of databases
        headers:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        db_list
    """
    db_list = []
    headers = {
        "command": "get databases",
        "User-Agent": "AnyLog/1.23"
    }

    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(error_type="GET", cmd=headers['command'], error=error)
    else:
        try:
            output = r.text
        except Exception as e:
            if exception is True:
                print(f"Failed to extract result for {headers['command']} (Exception: {e})")
        else:
            if output != 'No DBMS connections found':
                for row in output.split('\n'):
                    if 'sqlite' in row or 'psql' in row:
                        db_list.append(row.split(' ')[0].rstrip().lstrip())
    return db_list


def connect_dbms(anylog_conn:AnyLogConnection, db_name:str, db_type:str="sqlite", db_ip:str="!db_ip", db_port:str="!db_port",
                 db_user:str="!db_user", db_passwd:str="!db_passwd", exception:bool=False)->bool:
    """
    Connect to logical database
    :command:
        connect dbms {db_name} where type={db_type} and user={db_user} and password={db_passwd} and ip={db_ip} and port={db_port}
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        db_name:str - logical database name
        db_type:str - logical database type (ex SQLite or PSQL)
        db_ip:str - database IP address
        db_port:str - database port
        db_user:str - database user
        db_passwd:str - password correlated to database user
        exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    cmd = f"connect dbms {db_name} where type={db_type}"
    if db_type != 'sqlite':
        cmd += f" and ip={db_ip} and port={db_port} and user={db_user} and password={db_passwd}"

    headers = {
        'command': cmd,
        'User-Agent': 'AnyLog/1.23'
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r

def disconnect_dbms(anylog_conn:AnyLogConnection, db_name:str, exception:bool=False)->bool:
    """
    Disconnect database
    :command: 
        disconnect dbms {db_name} 
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        db_name:str - logical database name
        exception:bool - whether to print exception
    :params:
        headers:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return: 
        r
    """
    headers = {
        "command": f"disconnect dbms {db_name}",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def check_table(anylog_conn:AnyLogConnection, db_name:str, table_name:str, exception:bool=False)->bool:
    """
    Validate if table if exists
    :command:
        get table local status where dbms={db_name} and name={table_name}
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        db_name:str - logical database name
        table_name:str - table to check if exists
        exception:bool - whether to print exception
    :params:
        status:bool
        headers:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        if table exists return True, else False
    """
    status = False
    headers = {
        "command": f"get table local status where dbms={db_name} and name={table_name}",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(error_type="GET", cmd=headers['command'], error=error)
    else:
        try:
            if r.json()['local'] == 'true':
                status = True
        except:
            if 'true' in r.text:
                status = True
    return status


def create_table(anylog_conn:AnyLogConnection, db_name:str, table_name:str, exception:bool=False)->bool:
    f"""
    Create table based on params
    :command: 
        create table {table_name} where dbms={db_name}
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        db_name:str - logical database name
        table_name:str - table to create
        exception:bool - whether to print exception
    :params:
        headers:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    headers = {
        "command": f"create table {table_name} where dbms={db_name}",
        "User-Agent": "AnyLog/1.23"
    }

    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def set_partitions(anylog_conn:AnyLogConnection, db_name:str="!default_dbms", table:str="*",
                   partition_column:str="!partition_column", partition_interval:str="!partition_interval",
                   exception:bool=False)->bool:
    """
    Set partitions
    :command:
        partition !default_dbms * using !partition_column by !partition_interval
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        db_name:str - logical database to partition
        table:str - table to partition against, if set to '*' partition all tables in database
        partition_column:str - column to partition by
        partition_interval:str - partition interval
        exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    headers = {
        "command": f"partition {db_name} {table} using {partition_column} by {partition_interval}",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def check_partitions(anylog_conn:AnyLogConnection, exception:bool=False)->bool:
    """
    Check whether partitions already exist or not
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        status:bool
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        status - if partition DNE return False, else return True
    """
    status = False
    headers = {
        "command": "get partitions",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(error_type="GET", cmd=headers['command'], error=error)
    elif int(r.status_code) == 200:
        try:
            if r.text != 'No partitions declared':
                status = True
        except Exception as e:
            if exception is True:
                print(f'Failed to check whether partitions are set or not (Error {e})')
    return status


def execute_post_command(anylog_conn:AnyLogConnection, db_name:str, command:str, exception:bool=False)->bool:
    """
    Execute a (POST) command against SQL database
        - CREATE
        - INSERT
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        db_name:str - logical database to execute against
        command:str - SQL command to execute
        exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    headers = {
        "command": f'sql {db_name} {command}',
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)

    return r


def execute_get_command(anylog_conn:AnyLogConnection, db_name:str, command:str, format:str='json', stat:bool=False,
                        destination:str=None, exception:bool=False)->str:
    """
    Execute GET of a query
    :list of query options:
        https://github.com/AnyLog-co/documentation/blob/master/queries.md#query-options
    :args:
`       anylog_conn:AnyLogConnection - connection to AnyLog
        db_name:str - logical database to execute against
        command:str - SQL command to execute
        format:str - whether to print results as JSON or Table format
        stat:bool - whether to include query statistics
        destination:str - whether to set destination to "network" or an IP/port address
        exception:bool - whether to print exception
    :params:
        output:str - content to return
        sql_cmd:str - full command to execute
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        query result(s)
    """
    output = None
    if format not in ['json', 'table']:
        format = 'json'
    if not isinstance(stat, bool):
        stat=False

    sql_cmd = f'sql {db_name} format={format} and stat={str(stat).lower()} "{command}"'
    headers = {
        "command": sql_cmd,
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(error_type="GET", cmd=headers['command'], error=error)
    else:
        try:
            output = r.json()
        except:
            try:
                output = r.text
            except Exception as e:
                if exception is True:
                    print(f'Failed to extract results for query: "{command}" (Error: {e}')

    return output



