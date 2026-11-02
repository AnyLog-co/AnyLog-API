import asyncio
import json

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, exec_info, LevelMode, async_exec_logging

# Step 1: Check if logical database exists
async def async_list_databases(anylog_conn:AnyLogRest, is_json:bool=False, destination:str|None=None,
                               exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Get list of logical databases
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog
        is_json:bool - whether to return results in JSON format
        destination:str - remote destination
        exec_mode:ExecMode - Execution mode
    :return:
        databases and database type as either string (table) format or JSON
        if exec_mode isn't ExecMode.EXECUTE returns raw response-
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_list_databases)

    headers = {
        "command": f"get databases",
        "Anylog-Agent": "AnyLog/1.23",
        **({"destination": destination} if destination else {})
    }
    if is_json:
        headers["command"] += " where format=json"

    databases = await anylog_conn.async_post(headers={"Content-Type": "application/json"}, payload=json.dumps(headers),
                                             exec_mode=exec_mode)

    response = databases
    if exec_mode == ExecMode.EXECUTE and 200 <= int(databases.status_code) < 300:
        try:
            if databases.text.strip() == "No DBMS connections found":
                response = {}
            response = databases.json()
        except Exception:
            response = databases.text

    return response


def list_databases(anylog_conn:AnyLogRest, is_json:bool=False, destination:str|None=None,
                   exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Get list of logical databases
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog
        is_json:bool - whether to return results in JSON format
        destination:str - remote destination
        exec_mode:ExecMode - Execution mode
    :return:
        databases and database type as either string (table) format or JSON
    """
    return asyncio.run(async_list_databases(anylog_conn=anylog_conn, is_json=is_json, destination=destination,
                                            exec_mode=exec_mode))

async def async_is_database(anylog_conn:AnyLogRest, db_name:str, remote_destination:str|None=None,
                            exec_mode:ExecMode=ExecMode.EXECUTE)->bool:
    """
    check whether the logic database exists or not
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog
        db_name:str - logical database
        remote_destination:str - remote destination
        exec_mode:ExecMode - Execution mode
    :return:
        True if logical database exists
        False if logical database doesn't exist
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_is_database)

    databases = await async_list_databases(anylog_conn=anylog_conn, is_json=True, destination=remote_destination,
                                           exec_mode=exec_mode)

    if exec_mode == ExecMode.EXECUTE:
        return True if db_name in databases else False
    return databases


def is_database(anylog_conn:AnyLogRest, db_name:str, destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE)->bool:
    """
    check whether the logic database exists or not
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog
        db_name:str - logical database
        destination:str - remote destination
        exec_mode:ExecMode - Execution mode
    :return:
        True if logical database exists
        False if logical database doesn't exist
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=is_database)

    return asyncio.run(async_is_database(anylog_conn=anylog_conn, db_name=db_name, destination=destination,
                                         exec_mode=exec_mode))


# Step 2: Connect ot logical database
async def async_connect_dbms(anylog_conn:AnyLogRest, db_name:str, db_type:str, db_ip:str|None=None,
                             db_port:int|None=None, db_user:str|None=None, db_password:str|None=None,
                             in_memory:bool=False, destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Connect to logical database
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog
        db_name:str - logical database name
        db_type:str - logical database type
        db_ip:str - db IP
        db_port:int - db port
        db_user:str - db user
        db_password:str - db password
        in_memory:bool - whether to run in memory mode for SQLite or unlogged for PSQL
        exec_mode:ExecMode - Execution mode
    """
    supported_dbs = ["psql", "mongo", "sqlite"]

    if exec_mode == ExecMode.INFO:
        exec_info(func=async_connect_dbms)
    elif db_type not in supported_dbs:
        await async_exec_logging(
            message=f"Invalid db_type {db_type!r} - supported: {sorted(supported_dbs)}",
            level=LevelMode.ERROR,
            raise_exception=True
        )
        return None  # only reached if raise_exception doesn't actually raise
    elif exec_mode == ExecMode:
        check_db = async_is_database(anylog_conn=anylog_conn, db_name=db_name, destination=destination, exec_mode=exec_mode)
        if check_db:
            return None

    command = f"connect dbms {db_name} where type={db_type}"
    if db_ip:
        command += f" and ip={db_ip}"
    if db_port:
        command += f" and port={db_port}"
    if db_user:
        command += f" and user={db_user}"
    if db_password:
        command += f" and password={db_password}"
    if in_memory and db_type == "sqlite":
        command += " and memory=true"
    elif in_memory and db_type == "psql":
        command += " and unlog=true"

    headers = {
        "command": command,
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": destination} if destination else {})
    }

    return await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode)


def connect_dbms(anylog_conn:AnyLogRest, db_name:str, db_type:str, db_ip:str|None=None, db_port:int|None=None,
                 db_user:str|None=None, db_password:str|None=None, in_memory:bool=False, destination:str|None=None,
                 exec_mode:ExecMode=ExecMode.EXECUTE):
    """
   Connect to logical database
   :args:
       anylog_conn:AnyLogRest - connection to AnyLog
       db_name:str - logical database name
       db_type:str - logical database type
       db_ip:str - db IP
       db_port:int - db port
       db_user:str - db user
       db_password:str - db password
       in_memory:bool - whether to run in memory mode for SQLite or unlogged for PSQL
       exec_mode:ExecMode - Execution mode
   """
    return async_connect_dbms(anylog_conn=anylog_conn, db_name=db_name, db_type=db_type, db_ip=db_ip, db_port=db_port,
                              db_user=db_user, db_password=db_password, in_memory=in_memory, destination=destination,
                              exec_mode=exec_mode)


# Step 3: Check if table(s) exists
async def async_list_tables(anylog_conn:AnyLogRest, db_name:str, is_json:bool=False, destination:str|None=None,
                            exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Get list of tables on a given logical database
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog
        is_json:bool - whether to return results in JSON format
        destination:str - remote destination
        exec_mode:ExecMode - Execution mode
    :return:
        databases and database type as either string (table) format or JSON
        if exec_mode isn't ExecMode.EXECUTE returns raw response-
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_list_databases)

    headers = {
        "command": f"get tables where dbms={db_name} {'and format=json' if is_json is True else ''}",
        "Anylog-Agent": "AnyLog/1.23",
        **({"destination": destination} if destination else {})
    }


    tables = await anylog_conn.async_post(headers={"Content-Type": "application/json"}, payload=json.dumps(headers),
                                             exec_mode=exec_mode)

    response = tables
    if exec_mode == ExecMode.EXECUTE and 200 <= int(tables.status_code) < 300:
        try:
            response = tables.json()
        except Exception:
            response = tables.text

    return response


def list_tables(anylog_conn:AnyLogRest, db_name:str, is_json:bool=False, destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Get list of tables on a given logical database
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog
        is_json:bool - whether to return results in JSON format
        destination:str - remote destination
        exec_mode:ExecMode - Execution mode
    :return:
        databases and database type as either string (table) format or JSON
        if exec_mode isn't ExecMode.EXECUTE returns raw response-
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=list_tables)

    return asyncio.run(async_list_tables(anylog_conn=anylog_conn, db_name=db_name, is_json=is_json, destination=destination,
                                         exec_mode=exec_mode))


async def async_is_table(anylog_conn:AnyLogRest, db_name:str, table_name:str, destination:str|None=None,
                         exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Check whether a specific table exists
    :args:
        anylog_conn:AnyLogREST - REST connection to AnyLog
        db_name:str - logical database name
        table_name:str - logical table name
        destination:str - remote destination
        exec_mode:ExecuteMode - Execution mode
    :params:
        _tables_list:str - list of tables
        _is_table:bool - whether a table exists
    :return:
        if table exists locally return True
        if table doesn't return False
        all other cases None
    """
    _is_table = None
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_is_table)

    _tables_list = None
    if exec_mode == ExecMode.EXECUTE:
        _tables_list = await async_list_tables(anylog_conn=anylog_conn, db_name=db_name, is_json=True, destination=destination,
                                              exec_mode=exec_mode)

    if _tables_list and _tables_list.get(db_name):
        _is_table = _tables_list.get(db_name).get(table_name).get("local")
        # is_table = True if tables_list.get(db_name).get(table_name) else False
    elif exec_mode == ExecMode.EXECUTE:
        _is_table = False

    return _is_table


def is_table(anylog_conn:AnyLogRest, db_name:str, table_name:str, destination:str|None=None,
                         exec_mode:ExecMode=ExecMode.EXECUTE):

    return asyncio.run(async_is_table(anylog_conn=anylog_conn, db_name=db_name, table_name=table_name,
                                      destination=destination, exec_mode=exec_mode))

# Step 4: Create table

async def async_create_table(anylog_conn:AnyLogRest, db_name:str, table_name:str, destination:str|None=None,
                             exec_mode=ExecMode.EXECUTE):
    """
    Execute table based on create table
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog
        db_name:str - logical database name
        table_name:str - logic table name
        destination:str - remote destination

    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_create_table)

    elif exec_mode == ExecMode.EXECUTE:
        _is_table = await async_is_table(anylog_conn=anylog_conn, db_name=db_name, table_name=table_name,
                                         destination=destination, exec_mode=exec_mode)
        if _is_table:
            return None

    headers = {
        "command": f"create table {table_name} where dbms={db_name}",
        "Anylog-Agent": "AnyLog/1.23",
        **({"destination": destination} if destination else {})
    }

    return await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode)


def create_table(anylog_conn:AnyLogRest, db_name:str, table_name:str, destination:str|None=None,
                             exec_mode=ExecMode.EXECUTE):
    return asyncio.run(async_create_table(anylog_conn=anylog_conn, db_name=db_name, table_name=table_name,
                                          destination=destination, exec_mode=exec_mode))


