import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'python_rest'))

from anylog_connector import AnyLogConnector
import database_deployment
import scheduler_deployment
import blockchain_deployment

def main(anylog_conn:AnyLogConnector, anylog_configs:dict, exception:bool=False):
    """
    Main for deploying a master/ledger node
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        anylog_configs:dict - configurations
        exception:bool - whether to print exceptions
    """
    # connect to blockchain database and create ledger (if DNE)
    if database_deployment.declare_database(anylog_conn=anylog_conn, db_name='almgm',
                                            anylog_configs=anylog_configs, exception=exception) is False:
        print('Notice: Failed to connect to `almgm` logical database')

    if database_deployment.declare_table(anylog_conn=anylog_conn, db_name='almgm', table_name='tsd_info',
                                         exception=exception) is False:
        print(f'Notice: Failed to declare tsd_info in `almgm` logical database.')

    # deploy system_query if DNE
    if database_deployment.declare_database(anylog_conn=anylog_conn, db_name='system_query',
                                            anylog_configs=anylog_configs, exception=exception) is False:
        print('Notice: Failed to declare `system_query` logical database')

    # run scheduler 1
    if scheduler_deployment.run_scheduler1(anylog_conn=anylog_conn, exception=exception) is False:
        return False

    # run blockchain sync
    scheduler_deployment.run_blockchain_sync(anylog_conn=anylog_conn, anylog_configs=anylog_configs, exception=exception)

    # declare policy
    if blockchain_deployment.validate_node_policy(anylog_conn=anylog_conn, policy_type='publisher',
                                                  anylog_configs=anylog_configs, exception=exception) is False:
        blockchain_deployment.declare_node_policy(anylog_conn=anylog_conn, policy_type='publisher',
                                                  anylog_configs=anylog_configs, exception=exception)

    return True