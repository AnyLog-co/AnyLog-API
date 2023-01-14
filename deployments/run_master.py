import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'python_rest'))

from anylog_connector import AnyLogConnector
import database_deployment

def main(anylog_conn:AnyLogConnector, anylog_configs:dict, exception:bool=False):
    """
    Main for deploying a master/ledger node
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        anylog_configs:dict - configurations
        exception:bool - whether to print exceptions
    """
    # connect to blockchain database and create ledger (if DNE)
    if database_deployment.declare_database(anylog_conn=anylog_conn, db_name='blockchain',
                                            anylog_configs=anylog_configs, exception=exception) is False:
        print('Error: Failed to connect to `blockchain` logical database. Cannot continue with master deployment')
        return

    if database_deployment.declare_table(anylog_conn=anylog_conn, db_name='blockchain', table_name='ledger',
                                         exception=exception) is False:
        print(f'Error: Failed to declare ledger in `blockchain` logical database. Cannot continue with master deployment')
        return

    # deploy system_query if DNE
    if database_deployment.declare_database(anylog_conn=anylog_conn, db_name='system_query',
                                            anylog_configs=anylog_configs, exception=exception) is False:
        print('Notice: Failed to declare `system_query` logical database')

    # run scheduler 1
    

    # run blockchain sync

    # declare policy
    pass