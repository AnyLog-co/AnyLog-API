from anylog_connection import AnyLogConnection
from support import print_error


def connect_db(anylog_conn:AnyLogConnection, db_type:str, db_name:str, host:str=None, port:int=None, user:str=None,
               passwd:str=None, memory:bool=False, exception:bool=False)->bool:
    """
    Connect to logical database
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        db_type:str - physical database type
        db_name:str - logical database name
        host:str - database connection info
        port:int - database port
        user:str - connecting user
        passwd:str - password for database user
        memory:bool - run logical database against SQLite in memory. predominantly used in system_query.
        exception:bool - whether to print exception
    :params:
        status:bool
        headers:dict - REST header
        r:bool, error:str - whether the command failed & why
    :status:
        status
    """
    status = False
    headers ={
        "command": f"connect dbms {db_name} where type={db_type}",
        "User-Agent": "AnyLog/1.23"
    }

    if db_name != 'sqlite':
        headers['command'] += f" and ip={host} and port={port} and user={user} and password={passwd}"
    elif memory is True:
        headers['command'] += " and memory=true"

    # validate DB DNE
    if db_name in get_db(anylog_conn=anylog_conn, exception=exception):
        status = True

    while status is False:
        r, error = anylog_conn.post(headers=headers)
        if exception is True and r is False:
            print_error(error_type='POST', cmd=headers['command'], error=error)
        if r is False or db_name not in get_db(anylog_conn=anylog_conn, exception=exception):
            headers['command'] = f"connect dbms {db_name} where type=sqlite"
        else:
            status = True

    return status


def create_table(anylog_conn:AnyLogConnection, db_name:str, table_name:str, exception:bool=False)->bool:
    """
    Create table against a specific database - based on either hardcoded or based on what's on the blockchain
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        db_name:str - logical database name
        table_name:str - table name
        exception:bool - whether to print exception
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status = True
    headers ={
        "command": f"create table {table_name} where dbms={db_name}",
        "User-Agent": "AnyLog/1.23"
    }

    status, error = anylog_conn.post(headers=headers)
    if exception is True and status is False:
        print_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def get_db(anylog_conn:AnyLogConnection, exception:bool=False):
    """
    Get list of logical databases
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        databases_list:list - list of logical databases
        headers:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        databases_list
    """
    databases_list = []
    headers = {
        'command': 'get databases',
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(error_type='GET', cmd=headers['command'], error=error)
    elif r.text != "No DBMS connections found":
        for row in r.text.split('\n'):
            for physical_db in  ['sqlite', 'psql']:
                if physical_db in row:
                    databases_list.append(row.split()[0])

    return databases_list






