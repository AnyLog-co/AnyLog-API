import json

import anylog_connector
import blockchain
import database

import generic_post
import support


def deploy_node(anylog_conn:anylog_connector.AnyLogConnector, configuration:dict, exception:bool=False):
    """
    Deploy an AnyLog master node
    :process:
        1. create blockchain database if DNE
        2. create ledger table in blockchain database if DNE
        3. connect to system_query (used for querying data) if configured
        4. declare policy on the blockchain
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog via REST
        configuration:dict - configurations to be used
        exception:bool - whether to print exceptions
    :params:
        new_policy:dict - generated policy
        json_policy:str - new_policy as JSON string
    """
    scripts = []
    where_conditions = support.build_where_condition(configuration=configuration)
    policy = blockchain.get_policy(anylog_conn=anylog_conn, policy_type="master", where_conditions=where_conditions,
                                   bring_conditions="first", bring_values="[*][id]", separator=None, view_help=False)

    if len(policy) == 0:
        scripts.append(generic_post.run_scheduler(anylog_conn=anylog_conn, schedule_number=1, execute_cmd=False, view_help=False))
        scripts.append(blockchain.run_synchronizer(anylog_conn=anylog_conn, source=configuration['blockchain_source'],
                                           time=configuration['sync_time'],
                                           dest=configuration ['blockchain_destination'],
                                           connection=configuration['ledger_conn'], execute_cmd=False, view_help=False))
        scripts.append(support.connect_dbms(anylog_conn=anylog_conn, db_name='blockchain',
                                                       configurations=configuration, execute_cmd=False))
        scripts.append(database.create_table(anylog_conn=anylog_conn, db_name='blockchain', table_name='ledger',
                                             execute_cmd=False, view_help=False))

        if 'system_query' in configuration and configuration['system_query'] is True:
            scripts.append(database.check_database(anylog_conn=anylog_conn, db_name='system_query', execute_cmd=False, json_format=True))

        new_policy = blockchain.create_node_policy(anylog_conn=anylog_conn, policy_type="master",
                                                   configuration=configuration, cluster_id=None, scripts=scripts,
                                                   exception=exception)
        new_policy = support.serialize_row(data=new_policy)
        if blockchain.prepare_policy(anylog_conn=anylog_conn, policy=new_policy) is True:
            if blockchain.publish_policy(anylog_conn=anylog_conn, policy=new_policy, local=True,
                                         ledger_conn=configuration['ledger_conn'], blockchain=None) is False:
                print(f"Failed to declare policy {new_policy} in blockchain")
            else:
                policy = blockchain.get_policy(anylog_conn=anylog_conn, policy_type="master",
                                               where_conditions=where_conditions, bring_conditions="first",
                                               bring_values="[*][id]", separator=None, view_help=False)
    if len(policy) == 0:
        print(f"Failed to declare policy for master")
    elif generic_post.policy_config(anylog_conn=anylog_conn, policy_id=policy, destination=None, execute_cmd=True,
                                   view_help=False) is False:
        print(f"Failed to configure node {anylog_conn.conn} to run as a master node")







