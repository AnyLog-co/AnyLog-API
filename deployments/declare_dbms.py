import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'python_rest'))

from anylog_connection import AnyLogConnection
import database_calls


def create_table_by_dbms(anylog_conn:AnyLogConnection, db_name:str, table_name:str=None, exception:bool=False):
    """
    Create tables based on database
    :process:
        1. check if table exists (locally) - return if exists
        2. for non-blockchain/almgm check if table exists (blockchain) - return if exists
        3. create table
    :args:
        anylog_conn:AnyLogConnection - AnyLog REST connection information
        db_name:str - logical database name
        table_name:str - logical table name
        exception:bool - whether to print exceptions
    :params:
        status:bool
    """
    if table_name is None and db_name in ['blockchain', 'almgm']:
        if db_name == 'blockchain':
            table_name = 'ledger'
        elif db_name == 'almgm':
            table_name = 'tsd_info'
        if database_calls.check_tables(anylog_conn=anylog_conn, db_name=db_name, table_name=table_name,
                                       local=True, exception=exception) is False:
            if database_calls.create_table(anylog_conn=anylog_conn, db_name=db_name, table_name=table_name,
                                           exception=exception) is False:
                print(f'Failed to create table {table_name} against {db_name} logical database')
    else:
        local_table_status = database_calls.check_tables(anylog_conn=anylog_conn, db_name=db_name,
                                                         table_name=table_name, local=True, exception=exception)
        blockchain_table_status = database_calls.check_tables(anylog_conn=anylog_conn, db_name=db_name,
                                                              table_name=table_name, local=False, exception=exception)
        if local_table_status is False and blockchain_table_status is True:
            if database_calls.create_table(anylog_conn=anylog_conn, db_name=db_name, table_name=table_name,
                                           exception=exception) is False:
                print(f'Failed to create table {table_name} against {db_name} logical database')
        elif local_table_status is False and blockchain_table_status is False:
            print(f'Unknown table {db_name}.{table_name}, cannot execute create.')


def declare_database(anylog_conn:str, node_type:str, db_name:str, enable_nosql:bool=False, db_type:str='sqlite', 
                     host:str=None, port:int=None, user:str=None, password:str=None, system_query:bool=False, 
                     memory:bool=False, exception:bool=False):
    """
    validate whether (SQL) database exists, if not - connect
    :process:
        1. check if database exists
        2. connect to database - if fails (and not MongoDB) connect to SQLite
        3. create table
    :args:
        anylog_conn:AnyLogConnection - AnyLog REST connection information
        db_name:str - logical database to check if exists
        db_type:str - database type
        host:int - database connection host
        port:str - database connection port
        user:str - database connection user
        password:str - password associated with database user
        memory:bool - whether to run database in memory (usually SQLite)
        exception:bool - whether to print exceptions
    :params:
        status:bool
    """
    status = True
    if node_type in ['ledger', 'standalone', 'standalone-publisher']:
        if database_calls.check_database(anylog_conn=anylog_conn, db_name='blockchain', exception=exception) is False:
            if database_calls.connect_database(anylog_conn=anylog_conn, db_name='blockchain', db_type=db_type,
                                               enable_nosql=enable_nosql, host=host, port=port, user=user,
                                               password=password, memory=False, exception=exception) is True:
                create_table_by_dbms(anylog_conn=anylog_conn, db_name='blockchain', exception=exception)

    if node_type in ['operator', 'publisher', 'standalone', 'standalone-publisher']:
        if database_calls.connect_database(anylog_conn=anylog_conn, db_name='almgm', db_type=db_type,
                                           enable_nosql=enable_nosql, host=host, port=port, user=user,
                                           password=password, memory=False, exception=exception) is True:
            create_table_by_dbms(anylog_conn=anylog_conn, db_name='almgm', exception=exception)

    if node_type in ['operator', 'standalone']:
        database_calls.connect_database(anylog_conn=anylog_conn, db_name=db_name, db_type=db_type, enable_nosql=enable_nosql,
                                        host=host, port=port, user=user, password=password, memory=False,
                                        exception=exception)
    if system_query is True:
        database_calls.connect_database(anylog_conn=anylog_conn, db_name='system_query', db_type=db_type,
                                        enable_nosql=enable_nosql, host=host, port=port, user=user, password=password,
                                        memory=str(memory).lower(), exception=exception)



