from anylog_connection import AnyLogConnection
import support


def check_database(anylog_conn:AnyLogConnection, db_name:str, exception:bool=False)->bool:
    """
    Check if a database exists
    :args:
        anylog_conn:AnyLogConnection - AnyLog REST connection information
        db_name:str - logical database to check if exists
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True if exists, else False
    """
    status=False
    headers = {
        'command': 'get databases',
        'User-Agent': 'AnyLog/1.23'
    }

    r, error = anylog_conn.get(headers=headers)
    if r is False or int(r.status_code) != 200:
        if exception is True:
            support.print_rest_error(error_type='GET', cmd=headers['command'], error=error)
    else:
        if db_name in r.text:
            status = True

    return status


def check_tables(anylog_conn:AnyLogConnection, db_name:str, table_name:str, local:bool=True,
                 exception:bool=False)->bool:
    """
    check whether table exists
    :args:
        anylog_conn:AnyLogConnection - AnyLog REST connection information
        db_name:str - logical database
        table_name:str - table associated with logical table
        local:bool - check against local table if True, else against blockchain
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return :
        True if exists, else False
    """
    status = False
    table_source = 'blockchain'
    if local is True:
        table_source = 'local'

    headers = {
        'command': f'get tables where dbms={db_name} and format=json',
        'User-Agent': 'AnyLog/1.23'
    }

    r, error = anylog_conn.get(headers=headers)
    if r is False or int(r.status_code) != 200:
        if exception is True:
            support.print_rest_error(error_type='GET', cmd=headers['command'], error=error)
    else:
        try:
            tables = r.json()
        except Exception as json_error:
            try:
                tables = r.json()
            except Exception as txt_error:
                print(f'Failed to extract results for `{headers["cmd"]}` (JSON Error: {json_error} | Text Error: {txt_error})')
    if isinstance(tables, dict) and db_name in tables and db_name != '*':
        if table_name in tables[db_name]:
            status = tables[db_name][table_name][table_source]

    return status


def connect_database(anylog_conn:AnyLogConnection, db_name:str, db_type:str='sqlite', enable_nosql:bool=False,
                     host:str=None, port:int=None, user:str=None, password:str=None, memory:bool=False,
                     exception:bool=False)->bool:
    """
    connect to logical database
    :args:
        anylog_conn:AnyLogConnection - AnyLog REST connection information
        db_name:str - logical database to check if exists
        db_type:str - database type
        enable_nosql:str - whether connection is against a NoSQL database
        port:int - database connection host
        host:str - database connection port
        user:str - database connection user
        password:str - password associated with database user
        memory:bool - whether to run database in memory (usually SQLite)
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        whether database was connected successfully or not
    """
    status = False
    headers = {
        'command': f'connect dbms {db_name} where type={db_type}',
        'User-Agent': 'AnyLog/1.23'
    }
    if db_type != 'sqlite':
        if host is not None:
            headers['command'] += f' and ip={host}'
        if port is not None:
            headers['command'] += f' and port={port}'
        if user is not None:
            headers['command'] += f' and user={user}'
        if password is not None:
            headers['command'] += f' and password={password}'
    headers['command'] += f' and memory={memory}'

    r, error = anylog_conn.post(headers=headers, payload=None)
    if r is False or int(r.status_code) != 200:
        if exception is True:
            support.print_rest_error(error_type='POST', cmd=headers['command'], error=error)
    else:
        if enable_nosql is True:
            db_name = f'{db_name.strip()}_blobs'
        if check_database(anylog_conn=anylog_conn, db_name=db_name) is True:
            status = True
    if status is False and enable_nosql is False:
        status = connect_database(anylog_conn=anylog_conn, db_name=db_name, db_type='sqlite', memory=memory)

    return status


def create_table(anylog_conn:AnyLogConnection, db_name:str, table_name:str, exception:bool=False)->bool:
    """
    create table within a given database
    :args:
        anylog_conn:AnyLogConnection - AnyLog REST connection information
        db_name:str - logical database to check if exists
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True if table was created, False if fails
    """
    status = True
    headers = {
        'command': f'create table {table_name} where dbms={db_name}',
        'User-Agent': 'AnyLog/1.23'
    }

    r, error = anylog_conn.post(headers=headers, payload=None)
    if r is False or int(r.status_code) != 200:
        status = False
        if exception is True:
            support.print_rest_error(error_type='POST', cmd=headers['command'], error=error)

    return status
