from anylog_connector import AnyLogConnector
import database_calls


def check_db_exists(anylog_conn:AnyLogConnector, db_name:str, view_help:bool=False, exception:bool=False):
    """
    check if database exists
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database to view
        view_help:bool - whether to print help info for AnyLog command
        exception:bool - whether to print error messages
    :params:
        status:bool
        output:str - content from `get databases` request
    :return:
        exists True
        else False
    """
    status = False
    output = database_calls.get_databases(anylog_conn=anylog_conn, json_format=True, view_help=view_help, exception=exception)
    if 'No DBMS connections found' not in output and output is not None:
        if db_name in list(output.keys()):
            status = True

    return status


def check_table_exists(anylog_conn:AnyLogConnector, db_name:str, table_name:str, local:bool=False, view_help:bool=False,
                       exception:bool=False):
    """
    check if database exists
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database to view
        table_name:str - table to check if exists
        local:bool - check if table is found locally -- if fails to get tables in JSON dict format, we only check table exists
        view_help:bool - whether to print help info for AnyLog command
        exception:bool - whether to print error messages
    :params:
        status:bool
        output:str - content from `get databases` request
    :return:
        exists True
        else False
    """
    status = False
    output = database_calls.get_tables(anylog_conn=anylog_conn, json_format=True, view_help=view_help,
                                       exception=exception)

    if db_name in output:
        if isinstance(output, dict):
            tables = output[db_name]
            if table_name in tables:
                if table_name in tables:
                    status = True
                if local is True:
                    status = tables[table_name]['local']
        elif table_name in output:
            status = True

    return status


def connect_dbms_call(db_name:str, db_type:str, host:str=None, port:int=None, username:str=None, password:str=None,
                      memory:bool=False):
    """
    Generate `connect dbms` command
    :args:
        db_name:str - logical database name
        db_type:str - physical database type
        host:str - physical database IP address
        port:int - physical database port value
        username:str - database username
        password:str - password associated with database user
        memory:bool - whether the database should run in memory
    :params:
        command:str - generated AnyLog command
    :return:
        command
    """
    command = f'connect dbms {db_name} where type={db_type.lower()}'
    if host is not None:
        command += f' and ip={host}'
    if port is not None:
        command += f' and port={port}'
    if username is not None:
        command += f' and user={username}'
    if password is not None:
        command += f' and password={password}'
    if memory is True:
        command += f' and memory=true'

    return command