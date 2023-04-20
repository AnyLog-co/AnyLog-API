import anylog_connector
from generic_get import get_cmd
from generic_post import post_cmd


def check_database(anylog_conn:anylog_connector.AnyLogConnector, db_name:str=None, json_format:bool=False,
                   destination:str=None, execute_cmd:bool=True, view_help:bool=False):
    """
    Check whether database exists
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/sql%20setup.md#the-get-databases-command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - AnyLog connection
        db_name:str - logical database name
        json_format:bool - whether to get JSON format
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - whether to print help information
    :params:
        status:bool
        headers:dict - REST headers
        output - results from REST request
    :return:
        None - view help
        True/False - if db_name is not None
        output - output from command
    """
    command = "get databases"
    if json_format is True:
        command += " where format=json"

    output = get_cmd(anylog_conn=anylog_conn, command=command, destination=destination, execute_cmd=execute_cmd,
                     view_help=view_help)

    if db_name is not None:
        status = False
        if db_name in output:
            status = True
        return status

    return output


def check_table(anylog_conn:anylog_connector.AnyLogConnector, db_name:str, table_name:str=None, json_format:bool=False,
                destination:str=None, execute_cmd:bool=True, view_help:bool=False):
    """
    check whether table exists in a given database
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/sql%20setup.md#the-get-table-command-get-table-status
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - AnyLog connection
        db_name:str - logical database name
        table_name:str - table to check 
        json_format:bool - whether to get JSON format
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - whether to print help information
    :param:
        status:bool
        headers:dict - REST headers
        output - results from REST request
    :return:
        None - view help
        True/False - if db_name is not None
        output - output from command
    """
    command = f"get tables where dbms={db_name}",
    if json_format is True:
        command += " and format=json"

    output = get_cmd(anylog_conn=anylog_conn, command=command, destination=destination, execute_cmd=execute_cmd,
                     view_help=view_help)

    if table_name is not None:
        status = False
        if db_name in output:
            if table_name in output[db_name]:
                if "local" in output[db_name][table_name] and output[db_name][table_name]["local"] is True:
                    status = True
        return status

    return output


def connect_dbms(anylog_conn:anylog_connector.AnyLogConnector, db_name:str, db_type:str='sqlite', ip:str=None,
                 port:int=None, user:str=None, password=None, memory:bool=False,
                 destination:str=None, execute_cmd:bool=True, view_help:bool=False):
    """
    connect to logical database
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/sql%20setup.md#connecting-to-a-local-database
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - AnyLog connection
        db_name:str - The logical name of the database
        db_type:str - The physical database - One of the supported databases such as psql, sqlite
        ip:str - IP address for connecting to database
        port:int - database port
        user:str - username recognized by the database
        password;str - user dbms password
        memory:bool - whether database is in memory or not (usually with SQLite)
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - whether to print help information
    :params:
        status:bool
        headers:dict - REST headers
    :return:
        None - view help
        True - success
        False - fails
    """
    command = f"connect dbms {db_name} where type={db_type}",
    if ip is not None:
        command += f" and ip={ip}"
    if port is not None:
        command += f" and port={port}"
    if user is not None:
        command += f" and user={user}"
    if password is not None:
        command += f" and password={password}"
    if memory is True:
        command += f" and memory=true"

    return post_cmd(anylog_conn=anylog_conn, command=command, payload=None, destination=destination,
                    execute_cmd=execute_cmd, view_help=view_help)


def create_table(anylog_conn:anylog_connector.AnyLogConnector, db_name:str, table_name:str=None, destination:str=None,
                 execute_cmd:bool=True, view_help:bool=False):
    """
    Create table on a given database
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - AnyLog connection
        db_name:str - logical database name
        db_name:str - table to create on given database
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - whether to print help information
    :args:
        status:bool
        headers:dict - REST headers
    :return:
        None - view help
        True - success
        False - fails
    """
    command = f"create table {table_name} where dbms={db_name}",

    return post_cmd(anylog_conn=anylog_conn, command=command, payload=None, destination=destination,
                    execute_cmd=execute_cmd, view_help=view_help)
