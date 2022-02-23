from anylog_connection import AnyLogConnect
from support import print_error

def connect_dbms(anylog_conn:AnyLogConnect, db_name:str, db_type:str="sqlite", db_ip:str="!db_ip", db_port:str="!db_port",
                 db_user:str="!db_user", db_passwd:str="!db_passwd", exception:bool=False)->bool:
    """
    Connect to logical database
    :command:
        connect dbms blockchain where type=psql and user = !db_user and password = !db_passwd and ip = !db_ip and port = !db_port
    :args:
        anylog_conn:AnyLogConnect - connection to AnyLog
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
        cmd += f" and ip={db_ip} and port={db_port} and user={db_user} and password=${db_passwd}"
    headers ={
        'command': cmd,
        'User-Agent': 'AnyLog/1.23'
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def set_partitions(anylog_conn:AnyLogConnect, db_name:str="!default_dbms", table:str="*",
                   partition_column:str="!partition_column", partition_interval:str="!partition_interval",
                   exception:bool=False)->bool:
    """
    Set partitions
    :command:
        partition !default_dbms * using !partition_column by !partition_interval
    :args:
        anylog_conn:AnyLogConnect - connection to AnyLog
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

