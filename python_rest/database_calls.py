from anylog_connector import AnyLogConnector
import generic_get_calls
import database_support
import rest_support


def get_databases(anylog_conn:AnyLogConnector, json_format:bool=False, view_help:bool=False, exception:bool=False)->str:
    """
    Get list of databases
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/sql%20setup.md#the-get-databases-command
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        json_format:bool - whether to get results in JSON dictionary
        view_help:bool - whether to view help for command
        exception:bool - whether to print error messages
    :params:
        output:str - results from REST request
        headers:dict - REST header requests
        r:request.get, error:str - REST request results
    :return:
        if success returns content (output), else None
    """
    output = None
    headers = {
        'command': 'get databases',
        'User-Agent': 'AnyLog/1.23'
    }

    if json_format is True:
        headers['command'] += ' where format=json'

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        r, error = anylog_conn.get(headers=headers)
        if r is False and exception is True:
            rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            output = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    return output


def get_tables(anylog_conn:AnyLogConnector, db_name:str='*', json_format:bool=True, view_help:bool=False,
               exception:bool=False)->str:
    """
    View list of tables in database (if set)
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/sql%20setup.md#the-get-tables-command
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database to get tables for (if not set, then get all tables)
        json_format:bool - whether to get results in JSON dictionary
        view_help:bool - whether to view help for command
        exception:bool - whether to print error messages
    :params:
        output:str - results from REST request
        headers:dict - REST header requests
        r:request.get, error:str - REST request results
    :return:
        if success returns content (output), else None
    """
    output = None
    headers = {
        'command': f'get tables where dbms={db_name}',
        'User-Agent': 'AnyLog/1.23'
    }

    if json_format is True:
        headers['command'] += ' and format=json'

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        r, error = anylog_conn.get(headers=headers)
        if r is False and exception is True:
            rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            output = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    return output


def connect_database(anylog_conn:AnyLogConnector, db_name:str, db_type:str='sqlite', host:str=None, port:int=None,
                     user:str=None, password:str=None, memory:bool=False, view_help:bool=False, exception:bool=False)->bool:
    """
    connect to logical database
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/sql%20setup.md#connecting-to-a-local-database
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        db_name:str - logical database to check if exists
        db_type:str - database type
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
    status = None
    headers = {
        'command': database_support.connect_dbms_call(db_name=db_name, db_type=db_type, ip=host, port=port,
                                                      username=user, password=password, memory=memory),
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        r, error = anylog_conn.post(headers=headers, payload=None)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], exception=exception)

    return status


def create_table(anylog_conn:AnyLogConnector, db_name:str, table_name:str, view_help:bool=False,
                 exception:bool=False)->bool:
    """
    create table within a given database - as long as the `CREATE TABLE` statement exists in the blockchain
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        db_name:str - logical database to check if exists
        view_help:bool - whether to print information regarding function
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True if table was created, False if fails
    """
    status = None
    headers = {
        'command': f'create table {table_name} where dbms={db_name}',
        'User-Agent': 'AnyLog/1.23'
    }
    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        r, error = anylog_conn.post(headers=headers, payload=None)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status
