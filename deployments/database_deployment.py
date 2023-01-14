import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'python_rest'))

from anylog_connector import AnyLogConnector
import database_calls
import database_support


def declare_database(anylog_conn:AnyLogConnector, db_name:str, anylog_configs:dict, exception:bool=False)->bool:
    """
    Create logical database
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database name
        anylog_configs:dict  - AnyLog configurations (used to connect to database)
        exception:bool - whether to print exceptions
    :params:
        status:bool
        while_status:bool
        db_type:str - physical database type
        db_configs:dict - extracted database cconfigs form anylog_configs
        memory:bool - whether to run logical database (`system_query`) in memory
    :return:
        status - whether query was successful or not

    """
    status = True
    db_type = anylog_configs['db_type'].lower()
    if db_type == 'mongodb':
        db_type = 'mongo'
    elif db_type in ['postgres', 'postgresql']:
        db_type = 'psql'

    db_configs = {}
    for param in ['db_ip', 'db_port', 'db_user', 'db_password']:
        if param not in anylog_configs or anylog_configs[param] == '':
            db_configs[param] = None
        else:
            db_configs[param] = anylog_configs[param]

    memory = False
    if db_name == 'system_query':
        if 'memory' in anylog_configs and anylog_configs['memory'] is True:
            db_type = 'sqlite'
            memory = True

    is_database = database_support.check_db_exists(anylog_conn=anylog_conn, db_name=db_name, view_help=False,
                                                   exception=exception)
    while is_database is False:
        status = database_calls.connect_database(anylog_conn=anylog_conn, db_name=db_name, db_type=db_type,
                                                 host=db_configs['db_ip'], port=db_configs['db_port'],
                                                 user=db_configs['db_user'], password=db_configs['db_password'],
                                                 memory=memory, view_help=False, exception=exception)
        if db_type not in ['sqlite', 'mongo'] and status is False:
            db_type = 'sqlite'
        elif db_type == 'mongo' and status is False:
            print(f'Failed to connect to {db_name} against MongoDB physical database')
            is_database = True
        elif db_type == 'sqlite' and status is False:
            print(f'Failed to connect to {db_name} against SQLite physical database')
            is_database = True
        else:
            is_database = True

    return status


def declare_table(anylog_conn:AnyLogConnector, db_name:str, table_name:str, exception:bool=False)->bool:
    """
    Declare table in database if DNE
    :args:
        anylog_conn:AnyLogConnector - REST connection to AnyLog
        db_name:str - logical database name
        table_name;str - table name
        exception:bool - whether to print exceptions
    :params:
        status:bool
    :return:
        status
    """
    status = True
    if not database_support.check_table_exists(anylog_conn=anylog_conn, db_name=db_name, table_name=table_name,
                                               local=True, view_help=False, exception=exception):
        if not database_calls.create_table(anylog_conn=anylog_conn, db_name=db_name, table_name=table_name,
                                           view_help=False, exception=exception):
            status = False
            print(f'Failed to create table {table_name} in {db_name} logical database')

    return status

