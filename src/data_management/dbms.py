"""
Logical databases and tables - list, check, connect and create
"""
import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, build_headers, exec_info
from src.core.support_logging import LevelMode, async_exec_logging

SUPPORTED_DB_TYPES = ["psql", "mongo", "sqlite"]


# ---------------------------------------------------------------------------------------------------------------------
# Databases
# ---------------------------------------------------------------------------------------------------------------------
async def async_list_databases(anylog_conn:AnyLogRest, json_format:bool=False, remote_destination:str|None=None,
                               exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    List the logical databases the node is connected to
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        json_format:bool - return results in JSON format
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        get databases [where format=json]
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "get databases where format=json", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        databases and their type, as a table (str) or JSON; {} if the node has no databases
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_list_databases)

    headers = build_headers(command="get databases where format=json" if json_format else "get databases",
                            remote_destination=remote_destination)
    databases = await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)

    if exec_mode == ExecMode.EXECUTE and isinstance(databases, str) and databases.strip() == "No DBMS connections found":
        return {}
    return databases


def list_databases(anylog_conn:AnyLogRest, json_format:bool=False, remote_destination:str|None=None,
                   exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_list_databases` - see that function for details"""
    return asyncio.run(async_list_databases(anylog_conn=anylog_conn, json_format=json_format,
                                            remote_destination=remote_destination, exec_mode=exec_mode))


async def async_is_database(anylog_conn:AnyLogRest, db_name:str, remote_destination:str|None=None,
                            exec_mode:ExecMode=ExecMode.EXECUTE)->bool|str|None:
    r"""
    Check whether the node is connected to a logical database
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        db_name:str - logical database name
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        get databases where format=json
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "get databases where format=json", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        True if the database exists, otherwise False
        str / None - COMMAND / HELP mode
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_is_database)

    databases = await async_list_databases(anylog_conn=anylog_conn, json_format=True,
                                           remote_destination=remote_destination, exec_mode=exec_mode)
    if exec_mode != ExecMode.EXECUTE:
        return databases
    return bool(databases) and db_name in databases


def is_database(anylog_conn:AnyLogRest, db_name:str, remote_destination:str|None=None,
                exec_mode:ExecMode=ExecMode.EXECUTE)->bool|str|None:
    """Sync wrapper around `async_is_database` - see that function for details"""
    return asyncio.run(async_is_database(anylog_conn=anylog_conn, db_name=db_name,
                                         remote_destination=remote_destination, exec_mode=exec_mode))


async def async_connect_dbms(anylog_conn:AnyLogRest, db_name:str, db_type:str, db_ip:str|None=None,
                             db_port:int|None=None, db_user:str|None=None, db_password:str|None=None,
                             in_memory:bool=False, remote_destination:str|None=None,
                             exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Connect the node to a logical database - skipped if it's already connected
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        db_name:str - logical database name
        db_type:str - physical database type (psql, mongo, sqlite)
        db_ip:str - database IP
        db_port:int - database port
        db_user:str - database user
        db_password:str - database password
        in_memory:bool - SQLite: run in memory | PSQL: unlogged tables
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        connect dbms {db_name} where type={db_type} [and ip={db_ip}] [and port={db_port}] [and user={db_user}]
            [and password={db_password}] [and memory=true | unlog=true]
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: connect dbms mydb where type=psql and ip=127.0.0.1 and port=5432 and user=admin and password=passwd" \
          -H "AnyLog-Agent: AnyLog/1.23"
    :return:
        response from node, or None if already connected / invalid db_type
    :raise:
        ValueError - unsupported db_type (when FORCE_EXCEPTION is on)
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_connect_dbms)
    if db_type not in SUPPORTED_DB_TYPES:
        return await async_exec_logging(message=f"Invalid db_type {db_type!r} - supported: {SUPPORTED_DB_TYPES}",
                                        level=LevelMode.ERROR, exception_type=ValueError)
    if exec_mode == ExecMode.EXECUTE and await async_is_database(anylog_conn=anylog_conn, db_name=db_name,
                                                                 remote_destination=remote_destination,
                                                                 exec_mode=exec_mode):
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

    headers = build_headers(command=command, remote_destination=remote_destination)
    return await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode)


def connect_dbms(anylog_conn:AnyLogRest, db_name:str, db_type:str, db_ip:str|None=None, db_port:int|None=None,
                 db_user:str|None=None, db_password:str|None=None, in_memory:bool=False,
                 remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_connect_dbms` - see that function for details"""
    return asyncio.run(async_connect_dbms(anylog_conn=anylog_conn, db_name=db_name, db_type=db_type, db_ip=db_ip,
                                          db_port=db_port, db_user=db_user, db_password=db_password,
                                          in_memory=in_memory, remote_destination=remote_destination,
                                          exec_mode=exec_mode))


# ---------------------------------------------------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------------------------------------------------
async def async_list_tables(anylog_conn:AnyLogRest, db_name:str, json_format:bool=False,
                            remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    List the tables of a logical database
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        db_name:str - logical database name
        json_format:bool - return results in JSON format
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        get tables where dbms={db_name} [and format=json]
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "get tables where dbms=mydb and format=json", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        tables, as a table (str) or JSON
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_list_tables)

    command = f"get tables where dbms={db_name}" + (" and format=json" if json_format else "")
    headers = build_headers(command=command, remote_destination=remote_destination)
    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def list_tables(anylog_conn:AnyLogRest, db_name:str, json_format:bool=False, remote_destination:str|None=None,
                exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_list_tables` - see that function for details"""
    return asyncio.run(async_list_tables(anylog_conn=anylog_conn, db_name=db_name, json_format=json_format,
                                         remote_destination=remote_destination, exec_mode=exec_mode))


async def async_is_table(anylog_conn:AnyLogRest, db_name:str, table_name:str, remote_destination:str|None=None,
                         exec_mode:ExecMode=ExecMode.EXECUTE)->bool|str|None:
    r"""
    Check whether a table exists locally on the node
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        db_name:str - logical database name
        table_name:str - table name
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :params:
        tables:dict - `get tables` result ({db_name: {table_name: {"local": bool, ...}}})
    :cmd:
        get tables where dbms={db_name} and format=json
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "get tables where dbms=mydb and format=json", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        True if the table exists locally, otherwise False
        str / None - COMMAND / HELP mode
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_is_table)

    tables = await async_list_tables(anylog_conn=anylog_conn, db_name=db_name, json_format=True,
                                     remote_destination=remote_destination, exec_mode=exec_mode)
    if exec_mode != ExecMode.EXECUTE:
        return tables
    if not isinstance(tables, dict):
        return False
    return bool(((tables.get(db_name) or {}).get(table_name) or {}).get("local"))


def is_table(anylog_conn:AnyLogRest, db_name:str, table_name:str, remote_destination:str|None=None,
             exec_mode:ExecMode=ExecMode.EXECUTE)->bool|str|None:
    """Sync wrapper around `async_is_table` - see that function for details"""
    return asyncio.run(async_is_table(anylog_conn=anylog_conn, db_name=db_name, table_name=table_name,
                                      remote_destination=remote_destination, exec_mode=exec_mode))


async def async_create_table(anylog_conn:AnyLogRest, db_name:str, table_name:str, remote_destination:str|None=None,
                             exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Create a table in a logical database - skipped if it already exists
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        db_name:str - logical database name
        table_name:str - table name
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        create table {table_name} where dbms={db_name}
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: create table tsd_info where dbms=almgm" \
          -H "AnyLog-Agent: AnyLog/1.23"
    :return:
        response from node, or None if the table already exists
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_create_table)
    if exec_mode == ExecMode.EXECUTE and await async_is_table(anylog_conn=anylog_conn, db_name=db_name,
                                                              table_name=table_name,
                                                              remote_destination=remote_destination,
                                                              exec_mode=exec_mode):
        return None

    headers = build_headers(command=f"create table {table_name} where dbms={db_name}",
                            remote_destination=remote_destination)
    return await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode)


def create_table(anylog_conn:AnyLogRest, db_name:str, table_name:str, remote_destination:str|None=None,
                 exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_create_table` - see that function for details"""
    return asyncio.run(async_create_table(anylog_conn=anylog_conn, db_name=db_name, table_name=table_name,
                                          remote_destination=remote_destination, exec_mode=exec_mode))
