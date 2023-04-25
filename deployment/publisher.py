import anylog_connector
import blockchain
import database

import support
import generic_post
import declare_policy


def deploy_node(anylog_conn:anylog_connector.AnyLogConnector, configuration:dict, scripts:list=[],
                policy_deployment:bool=False, exception:bool=False):
    """
    """
    where_conditions = {
        "name": f'{configuration["node_name"]}-configs',
        "company": configuration["company_name"]
    }

    declare_policy.declare_node(anylog_conn=anylog_conn, node_type="master", configuration=configuration,
                                cluster_id=None, exception=exception)

    if policy_deployment is True:
        policy_id = blockchain.get_policy(anylog_conn=anylog_conn, policy_type="config",
                                          where_conditions=where_conditions, bring_conditions="first",
                                          bring_values="[*][id]", separator=None, destination=None, execute_cmd=True,
                                          view_help=False)
        if not policy_id:
            scripts.append(database.connect_dbms(anylog_conn=anylog_conn, db_name="blockchain",
                                                 db_type=configuration["db_type"], ip=configuration["db_ip"],
                                                 port=configuration["db_port"], user=configuration["db_user"],
                                                 password=configuration["db_passwd"], memory=False, destination=None,
                                                 execute_cmd=False, view_help=False))
            scripts.append(database.create_table(anylog_conn=anylog_conn, db_name="blockchain", table_name="ledger",
                                                 destination=None, execute_cmd=False, view_help=False))

            if configuration["system_query"] is True:
                db_type = "sqlite"
                if configuration["memory"] is False:
                    db_type = configuration["db_type"]
                scripts.append(database.connect_dbms(anylog_conn=anylog_conn, db_name="system_query",
                                                     db_type=db_type, ip=configuration["db_ip"],
                                                     port=configuration["db_port"], user=configuration["db_user"],
                                                     password=configuration["db_passwd"], memory=configuration["memory"],
                                                     destination=None, execute_cmd=False, view_hel=False))
            new_policy = blockchain.create_config_policy(configs=where_conditions, scripts=scripts)
            declare_policy.blockchain_store_policy(anylog_conn=anylog_conn, new_policy=new_policy,
                                                   ledger_conn=configuration["ledger_conn"])
            policy_id = blockchain.get_policy(anylog_conn=anylog_conn, policy_type="config",
                                              where_conditions=where_conditions, bring_conditions="first",
                                              bring_values="[*][id]", separator=None, destination=None,
                                              execute_cmd=True,
                                              view_help=False)
        if generic_post.policy_config(anylog_conn=anylog_conn, policy_id=policy_id, destination=None, execute_cmd=True,
                                        view_help=False) is False:
            print(f"Failed to configure node {anylog_conn.conn} to run as a master node")

    else:
        status = True
        if database.check_database(anylog_conn=anylog_conn, db_name='blockchain', json_format=True) is False:
            if database.connect_dbms(anylog_conn=anylog_conn, db_name="blockchain",
                                             db_type=configuration["db_type"], ip=configuration["db_ip"],
                                             port=configuration["db_port"], user=configuration["db_user"],
                                             password=configuration["db_passwd"], memory=False, destination=None,
                                             execute_cmd=True, view_hel=False) is False:
                status = False
                print(f"Failed to create logical database 'blockchain'. Cannot Continue")

        if status is True and database.check_table(anylog_conn=anylog_conn, db_name='blockchain', table_name='ledger',
                                                    json_format=True, view_help=False) is False:
            if database.create_table(anylog_conn=anylog_conn, db_name="blockchain", table_name="ledger",
                                     destination=None, execute_cmd=True, view_help=False) is False:
                print(f"Failed to create table blockchain.ledger. Cannot Continue")

        if configuration['system_query'] is True:
            if database.check_database(anylog_conn=anylog_conn, db_name='system_query', json_format=True) is False:
                db_type = "sqlite"
                if configuration["memory"] is False:
                    db_type = configuration["db_type"]
                if database.connect_dbms(anylog_conn=anylog_conn, db_name="system_query",
                                         db_type=db_type, ip=configuration["db_ip"],
                                         port=configuration["db_port"], user=configuration["db_user"],
                                         password=configuration["db_passwd"], memory=False, destination=None,
                                         execute_cmd=True, view_hel=False) is False:
                    print(f"Failed to create logical database 'blockchain'. Cannot Continue")









