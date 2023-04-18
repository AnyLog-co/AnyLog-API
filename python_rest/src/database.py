import anylog_connector


def check_database(anylog_conn:anylog_connector.AnyLogConnector, db_name:str=None, json_format:bool=False,
                   view_help:bool=False):
    """
    Check whether database exists
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/sql%20setup.md#the-get-databases-command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - AnyLog connection
        db_name:str - logical database name
        json_format:bool - whether to get JSON format
        view_help:bool - whether to print help information regarding command
    :params:
        status:bool
        headers:dict - REST headers
        output - results from REST request
    :return:
        None - view help
        True/False - if db_name is not None
        output - output from command
    """
    headers = {
        "command": "get databases",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(anylog_conn=anylog_conn, cmd=headers['command'])
        return None
    if json_format is True:
        headers["command"] += " where format=json"

    output = anylog_conn.get(headers=headers)
    if db_name is not None:
        status = False
        if db_name in output:
            status = True
        return status
    else:
        return output


def check_table(anylog_conn:anylog_connector.AnyLogConnector, db_name:str, table_name:str=None, json_format:bool=False,
                view_help:bool=False):
    """
    check whether table exists in a given database
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/sql%20setup.md#the-get-table-command-get-table-status
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - AnyLog connection
        db_name:str - logical database name
        table_name:str - table to check 
        json_format:bool - whether to get JSON format
        view_help:bool - whether to print help information regarding command
    :param:
        status:bool
        headers:dict - REST headers
        output - results from REST request
    :return:
        None - view help
        True/False - if db_name is not None
        output - output from command
    """
    status = False
    headers = {
        "command": f"get tables where dbms={db_name}",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(anylog_conn=anylog_conn, cmd=headers['command'])
        return None
    if json_format is True:
        headers["command"] += " and format=json"

    output = anylog_conn.get(headers=headers)
    if table_name is not None:
        if db_name in output:
            if table_name in output[db_name]:
                if "local" in output[db_name][table_name] and output[db_name][table_name]["local"] is True:
                    status = True
    else:
        return output

    return status


def connect_dbms(anylog_conn:anylog_connector.AnyLogConnector, db_name:str, db_type:str='sqlite', ip:str=None,
                 port:int=None, user:str=None, password=None, memory:bool=False, view_help:bool=False):
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
        view_help:bool - whether to print help information regarding command
    :params:
        status:bool
        headers:dict - REST headers
    :return:
        None - view help
        True - success
        False - fails
    """
    status = True
    headers = {
        "command": f"connect dbms {db_name} where type={db_type}",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(anylog_conn=anylog_conn, cmd=headers['command'])
        return None

    if ip is not None:
        headers['command'] += f" and ip={ip}"
    if port is not None:
        headers['command'] += f" and port={port}"
    if user is not None:
        headers['command'] += f" and user={user}"
    if password is not None:
        headers['command'] += f" and password={password}"
    if memory is True:
        headers['command'] += f" and memory=true"

    r = anylog_conn.post(headers=headers)
    if r is None or int(r.status_code) != 200:
        status = False

    return status


def create_table(anylog_conn:anylog_connector.AnyLogConnector, db_name:str, table_name:str=None, view_help:bool=False):
    """
    Create table on a given database
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - AnyLog connection
        db_name:str - logical database name
        db_name:str - table to create on given database
        view_help:bool - whether to print help information regarding command
    :args:
        status:bool
        headers:dict - REST headers
    :return:
        None - view help
        True - success
        False - fails
    """
    status = True
    headers = {
        "command": f"create table {table_name} where dbms={db_name}",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(anylog_conn=anylog_conn, cmd=headers['command'])
        return None

    r = anylog_conn.post(headers=headers)
    if r is None or int(r.status_code) != 200:
        status = False

    return status
