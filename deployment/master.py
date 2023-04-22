import anylog_connector
import blockchain
import database
import generic_post
import support


import json

def deploy_node(anylog_conn:anylog_connector.AnyLogConnector, configuration:dict, scripts:list=[],
                policy_deployment:bool=False, exception:bool=False):
    """
    
    """
    where_conditions = support.build_where_condition(configuration=configuration)
    policy = blockchain.get_policy(anylog_conn=anylog_conn, policy_type="master", where_conditions=where_conditions,
                                      bring_conditions="first", bring_values="[*][id]", execute_cmd=True)
    if len(policy) == 0: # ie no policy
        new_policy = blockchain.create_node_policy(anylog_conn=anylog_conn, policy_type="master",
                                                   configuration=configuration, cluster_id=None, scripts=scripts,
                                                   exception=exception)
        new_policy = support.serialize_row(data=new_policy)
        if blockchain.prepare_policy(anylog_conn=anylog_conn, policy=new_policy) is True:
            if blockchain.publish_policy(anylog_conn=anylog_conn, policy=new_policy, local=True,
                                         ledger_conn=configuration['ledger_conn'], blockchain=None) is False:
                print(f"Failed to declare policy {new_policy} in blockchain")

    if policy_deployment is False:
        pass
    elif policy_deployment is True:
        where_conditions['name'] = f"{configuration['node_name']}-configs"
        policy = blockchain.get_policy(anylog_conn=anylog_conn, policy_type="config",
                                          where_conditions=where_conditions, bring_conditions="first",
                                          bring_values="[*][id]", execute_cmd=True)
        if len(policy) == 0:
            scripts.append(support.connect_dbms(anylog_conn=anylog_conn, db_name='blockchain',
                                                configurations=configuration, execute_cmd=False))
            scripts.append(database.create_table(anylog_conn=anylog_conn, db_name='blockchain', table_name='ledger',
                                                 execute_cmd=False, view_help=False))

            if 'system_query' in configuration and configuration['system_query'] is True:
                scripts.append(database.check_database(anylog_conn=anylog_conn, db_name='system_query',
                                                      execute_cmd=False, json_format=True))
            new_policy = blockchain.create_config_policy(configs=where_conditions, scripts=scripts)
            new_policy = support.serialize_row(data=new_policy)

            if blockchain.prepare_policy(anylog_conn=anylog_conn, policy=new_policy) is True:
                if blockchain.publish_policy(anylog_conn=anylog_conn, policy=new_policy, local=True,
                                             ledger_conn=configuration['ledger_conn'], blockchain=None) is False:
                    print(f"Failed to declare policy {new_policy} in blockchain")
            policy = blockchain.get_policy(anylog_conn=anylog_conn, policy_type="config",
                                           where_conditions=where_conditions, bring_conditions="first",
                                           bring_values="[*][id]", execute_cmd=True)

        if len(policy) == 0 or generic_post.policy_config(anylog_conn=anylog_conn, policy_id=policy) is False:
            print(f"Failed to declare node based on policy ID - {policy}")






