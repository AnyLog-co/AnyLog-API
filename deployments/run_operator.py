import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'python_rest'))

from anylog_connector import AnyLogConnector
import generic_data_calls
import database_deployment
import scheduler_deployment
import blockchain_deployment
import publisher_operator_deployment

def main(anylog_conn:AnyLogConnector, anylog_configs:dict, exception:bool=False):
    """
    Main for deploying a operator node
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        anylog_configs:dict - configurations
        exception:bool - whether to print exceptions
    """
    # connect to logical databasebase
    status = True
    if 'default_dbms' in anylog_configs:
        if database_deployment.declare_database(anylog_conn=anylog_conn, db_name=anylog_configs['default_dbms'],
                                                anylog_configs=anylog_configs, exception=exception) is False:
            status = False
    else:
        status = False
    if status is False:
        print(f"Error: Failed to connect to default dbms `{anylog_configs['default_dbms']}` "
                +"logical database. Cannot continue")
        return status

    # connect to almgm database and create tsd_info (if DNE)
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
    policy_id = blockchain_deployment.validate_cluster_policy(anylog_conn=anylog_conn, anylog_configs=anylog_configs,
                                                              exception=exception)
    if policy_id == '':
        blockchain_deployment.declare_cluster_policy(anylog_conn=anylog_conn, anylog_configs=anylog_configs,
                                                     exception=exception)
        policy_id = blockchain_deployment.validate_cluster_policy(anylog_conn=anylog_conn, anylog_configs=anylog_configs,
                                                                  exception=exception)
    anylog_configs['cluster_id'] = policy_id
    if blockchain_deployment.validate_node_policy(anylog_conn=anylog_conn, policy_type='operator',
                                                  anylog_configs=anylog_configs, exception=exception) is False:
        blockchain_deployment.declare_node_policy(anylog_conn=anylog_conn, policy_type='operator',
                                                  anylog_configs=anylog_configs, exception=exception)

    if 'enable_partitions' in anylog_configs and anylog_configs['enable_partitions'] is True:
        if generic_data_calls.get_partitions(anylog_conn=anylog_conn, view_help=False, exception=exception) is False:
            if database_deployment.set_partions(anylog_conn=anylog_conn, anylog_configs=anylog_configs,
                                                 exception=exception) is False:

                print('Notice: Failed to set partitions')
            else:
                if scheduler_deployment.enable_delete_partitions(anylog_conn=anylog_conn, anylog_configs=anylog_configs,
                                                              exception=exception) is False:
                    print('Notice: Failed to declare scheduled process for cleaning partitions')

    # set buffer threshold  and streamer
    publisher_operator_deployment.declare_buffer_threshold(anylog_conn=anylog_conn, anylog_configs=anylog_configs,
                                                           exception=exception)

    publisher_operator_deployment.enable_streaming(anylog_conn=anylog_conn, exception=exception)

    # start operator
    return publisher_operator_deployment.run_operator(anylog_conn=anylog_conn, anylog_configs=anylog_configs,
                                                      exception=exception)

