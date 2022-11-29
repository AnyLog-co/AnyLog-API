import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from anylog_connection import AnyLogConnection
import database_calls as database_calls


def __declare_blockchain_db(anylog_conn:AnyLogConnection, db_type:str, host:str=None, port:int=None,
                            user:str=None, passwd:str=None, memory:bool=False, exception:bool=False):
    """
    Declare `blockchain` database + `ledger` table
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        db_type:str - physical database type
        host:str - database IP address
        port:str - database port
        user:str - database user
        passwd:str - password associated with user
        memory:bool - whether or not to have database in memory (SQLite)
        exception:bool - whether or not to print error messages
    :params:
        db_list:list - list of logical databases
    """
    db_list = database_calls.get_db(anylog_conn=anylog_conn, exception=exception)
    if 'blockchain' not in db_list:
        if db_type == 'sqlite':
            status = database_calls.connect_db(anylog_conn=anylog_conn, db_type=db_type, db_name='blockchain',
                                               host=None, port=None, user=None, passwd=None, memory=memory,
                                               exception=exception)
        else:
            status = database_calls.connect_db(anylog_conn=anylog_conn, db_type=db_type, db_name='blockchain',
                                               host=host, port=port, user=user,
                                               passwd=passwd, memory=memory, exception=exception)
        if status is False:
            print(f"Failed to connect to logical database blockchain. Unable to continue")
            exit(1)

    db_list = database_calls.get_db(anylog_conn=anylog_conn, exception=exception)
    if 'blockchain' in db_list:
        if not database_calls.create_table(anylog_conn=anylog_conn, db_name='blockchain', table_name='ledger', exception=exception):
            print('Failed to create ledger table on blockchain database. Unable to continue')
            exit(1)

def __declare_default_db(anylog_conn:AnyLogConnection, db_type:str, db_name:str, host:str=None, port:int=None,
                            user:str=None, passwd:str=None, memory:bool=False, exception:bool=False):

    """
    Declare logical database used by operator to store data
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        db_type:str - physical database type
        db_name:str - logical database name
        host:str - database IP address
        port:str - database port
        user:str - database user
        passwd:str - password associated with user
        memory:bool - whether or not to have database in memory (SQLite)
        exception:bool - whether or not to print error messages
    :params:
        db_list:list - list of logical databases
    """
    db_list = database_calls.get_db(anylog_conn=anylog_conn, exception=exception)
    if db_name not in db_list:
        if db_type == 'sqlite':
            status = database_calls.connect_db(anylog_conn=anylog_conn, db_type=db_type, db_name=db_name,
                                               host=None, port=None, user=None, passwd=None, memory=memory,
                                               exception=exception)
        else:
            status = database_calls.connect_db(anylog_conn=anylog_conn, db_type=db_type, db_name=db_name,
                                               host=host, port=port, user=user,
                                               passwd=passwd, memory=memory, exception=exception)
        if status is False:
            print(f"Failed to connect to logical database {db_name}. Unable to continue")
            exit(1)

def __declare_almgm_db(anylog_conn:AnyLogConnection, db_type:str, host:str=None, port:int=None, user:str=None,
                       passwd:str=None, memory:bool=False, exception:bool=False):
    """
    Declare `almgm` database + `tsd_info` table
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        db_type:str - physical database type
        host:str - database IP address
        port:str - database port
        user:str - database user
        passwd:str - password associated with user
        memory:bool - whether or not to have database in memory (SQLite)
        exception:bool - whether or not to print error messages
    :params:
        db_list:list - list of logical databases
    """
    db_list = database_calls.get_db(anylog_conn=anylog_conn, exception=exception)
    if 'almgm' not in db_list:
        if db_type == 'sqlite':
            status = database_calls.connect_db(anylog_conn=anylog_conn, db_type=db_type, db_name='almgm',
                                               host=None, port=None, user=None, passwd=None, memory=memory,
                                               exception=exception)
        else:
            status = database_calls.connect_db(anylog_conn=anylog_conn, db_type=db_type, db_name='almgm',
                                               host=host, port=port, user=user,
                                               passwd=passwd, memory=memory, exception=exception)
        if status is False:
            print(f"Failed to connect to logical database almgm. Unable to continue")
            exit(1)

    db_list = database_calls.get_db(anylog_conn=anylog_conn, exception=exception)
    if 'almgm' in db_list:
        if not database_calls.create_table(anylog_conn=anylog_conn, db_name='almgm', table_name='tsd_info', exception=exception):
            print('Failed to create tsd_info table on almgm table. Unable to continue')
            exit(1)


def __declare_system_query_db(anylog_conn:AnyLogConnection, db_type:str, host:str=None, port:int=None,
                            user:str=None, passwd:str=None, memory:bool=False, exception:bool=False):

    """
    Declare logical system_query used by operator to store data
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        db_type:str - physical database type
        db_name:str - logical database name
        host:str - database IP address
        port:str - database port
        user:str - database user
        passwd:str - password associated with user
        memory:bool - whether or not to have database in memory (SQLite)
        exception:bool - whether or not to print error messages
    :params:
        db_list:list - list of logical databases
    """
    db_list = database_calls.get_db(anylog_conn=anylog_conn, exception=exception)
    if 'system_query' not in db_list:
        if db_type == 'sqlite':
            status = database_calls.connect_db(anylog_conn=anylog_conn, db_type=db_type, db_name='system_query',
                                               host=None, port=None, user=None, passwd=None, memory=memory,
                                               exception=exception)
        else:
            status = database_calls.connect_db(anylog_conn=anylog_conn, db_type=db_type, db_name='system_query',
                                               host=host, port=port, user=user,
                                               passwd=passwd, memory=memory, exception=exception)
        if status is False:
            print(f"Failed to connect to logical database system_query.")
            

def deploy_dbms(anylog_conn:AnyLogConnection, node_type:str, db_type:str, db_name:str=None, host:str=None,
                port:int=None, user:str=None,passwd:str=None, system_query:bool=False, memory:bool=False,
                exception:bool=False):
    """
    Main process for deploying logical databases 
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        db_type:str - physical database type
        db_name:str - logical database name
        host:str - database IP address
        port:str - database port
        user:str - database user
        passwd:str - password associated with user
        system_query:bool - whether or not to deploy system_query
        memory:bool - whether or not to have database in memory (SQLite)
        exception:bool - whether or not to print error messages
    """
    
    if node_type in ['ledger', 'standalone', 'standalone-publisher']:
        __declare_blockchain_db(anylog_conn=anylog_conn, db_type=db_type, host=host, port=port, user=user,
                                passwd=passwd, memory=False, exception=exception)

    if node_type in ['operator', 'standalone']:
        __declare_default_db(anylog_conn=anylog_conn, db_type=db_type, db_name=db_name, host=host, port=port, user=user,
                             passwd=passwd, memory=False, exception=exception)

    if node_type in ['operator', 'publisher', 'standalone', 'standalone-publisher']:
        __declare_almgm_db(anylog_conn=anylog_conn, db_type=db_type, host=host, port=port, user=user,
                                passwd=passwd, memory=False, exception=exception)

    if system_query is True:
        __declare_system_query_db(anylog_conn=anylog_conn, db_type='sqlite', host=host, port=port, user=user, 
                                  passwd=passwd, memory=memory, exception=exception)
        
