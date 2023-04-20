import json

import anylog_connector
import blockchain
import database

import deployment_support


def deploy_node(anylog_conn:anylog_connector.AnyLogConnector, configuration:dict, exception:bool=False):
    """
    Deploy an AnyLog master node
    :process:
        1. create almgm database
        2. connect to system_query (used for querying data) if configured
        3. declare policy on the blockchain
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog via REST
        configuration:dict - configurations to be used
        exception:bool - whether to print exceptions
    :params:
        new_policy:dict - generated policy
        json_policy:str - new_policy as JSON string
    """
    if database.check_database(anylog_conn=anylog_conn,  db_name='almgm', json_format=True) is False:
        if deployment_support.connect_dbms(anylog_conn=anylog_conn, db_name='almgm', configurations=configuration) is False:
            status = False
            print(f"Failed to create logical database 'blockchain'. Cannot Continue")
            exit(1)

    if 'system_query' in configuration and configuration['system_query'] is True:
        if database.check_database(anylog_conn=anylog_conn, db_name='system_query', json_format=True) is False:
            if deployment_support.connect_dbms(anylog_conn=anylog_conn, db_name='system_query',
                                               configurations=configuration) is False:
                status = False
                print(f"Failed to create logical database 'system_query'. Cannot Continue")
                exit(1)

    if len(blockchain.get_policy(anylog_conn=anylog_conn, policy_type="publisher",
                                 where_conditions={"company": configuration['company_name']},
                                 bring_conditions=None, bring_values=None, separator=None, view_help=False)) == 0:
        new_policy = blockchain.create_node_policy(anylog_conn=anylog_conn, policy_type="publsiher", configuration=configuration,
                                                   cluster_id=None, exception=exception)
        try:
            json_policy = json.dumps(new_policy)
        except Exception as error:
            print(f"Failed to convert publisher node policy to JSON format (Error: {error})")
        else:
            if blockchain.prepare_policy(anylog_conn=anylog_conn, policy=json_policy) is True:
                if blockchain.publish_policy(anylog_conn=anylog_conn, policy=json_policy, local=True,
                                             ledger_conn=configuration['ledger_conn'], blockchain=None) is False:
                    print(f"Failed to declare policy {json_policy} in blockchain")
        






