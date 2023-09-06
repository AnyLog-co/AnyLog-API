import anylog_connector
import blockchain
import find_location

import support


def blockchain_store_policy(anylog_conn:anylog_connector.AnyLogConnector, new_policy:dict, ledger_conn:str):
    json_policy = support.serialize_row(data=new_policy)
    blockchain.prepare_policy(anylog_conn=anylog_conn, policy=json_policy)
    blockchain.publish_policy(anylog_conn=anylog_conn, policy=json_policy, local=True, ledger_conn=ledger_conn,
                              blockchain=None)


def declare_cluster(anylog_conn:anylog_connector.AnyLogConnector, configuration:dict, ignore_db:bool=False):
    """
    Declare cluster policy
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog via REST
        configuration:dict - node configuration
        ignore_db:bool - whether to ignore db in policy creation
    :params:
        where_conditions:dict - conditions to check based
        policy:str - policy (ID)
        new_policy:dict - generated policy
        json_policy:str - JSON string of new_policy
    :return:
        policy
    """
    where_conditions = {
        "name": configuration["cluster_name"],
        "company": configuration["company_name"]
    }
    if ignore_db is False:
        db_name = configuration["default_dbms"]

    policy = blockchain.get_policy(anylog_conn=anylog_conn, policy_type="cluster",
                                   where_conditions=where_conditions,
                                   bring_conditions="first", bring_values="[*][id]", separator=None, view_help=False)

    if not policy:
        new_policy = blockchain.create_cluster_policy(name=configuration["cluster_name"],
                                                      company_name=configuration["company_name"], db_name=db_name,
                                                      table_name=None)

        json_policy = support.serialize_row(data=new_policy)
        if blockchain.prepare_policy(anylog_conn=anylog_conn, policy=json_policy) is True:
            if blockchain.publish_policy(anylog_conn=anylog_conn, policy=json_policy, local=True,
                                         ledger_conn=configuration['ledger_conn'], blockchain=None) is False:
                print(f"Failed to declare policy {json_policy} in blockchain")
        else:
            print(f"Failed to declare policy {json_policy} in blockchain")

        policy = blockchain.get_policy(anylog_conn=anylog_conn, policy_type="cluster",
                                       where_conditions=where_conditions,
                                       bring_conditions="first", bring_values="[*][id]", separator=None,
                                       view_help=False)

    return policy


def declare_node(anylog_conn:anylog_connector.AnyLogConnector, node_type:str, configuration:dict, cluster_id:str=None,
                 exception:bool=False):
    """
    Declare node policy of type - master/operator/query/publisher
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        node_type:str - Node type
        configuration:dict - configurations
        cluster:str - cluster ID
        exception:bool - whether to print exception
    :params:
        where_conditions:dict - from configurations, generate where conditions
        policy:list - whether policy exists
        new_policy:dict  - generated policy
        json_policy:str - new_policy as JSON string
    """
    cluster_id = None
    where_conditions = support.build_where_condition(configuration=configuration)

    policy = blockchain.get_policy(anylog_conn=anylog_conn, policy_type=node_type,
                                   where_conditions=where_conditions,
                                   bring_conditions="first", bring_values="[*][id]", separator=None, view_help=False)

    if not policy:
        broker_port = None
        proxy_ip = None
        if "broker_port" in configuration:
            broker_port = configuration["broker_port"]
        if "proxy_ip" in configuration:
            proxy_ip = configuration["proxy_ip"]

        location, country, state, city = find_location.get_location(anylog_conn=anylog_conn, exception=exception)

        new_policy = blockchain.create_node_policy(policy_type=node_type, node_name=configuration["node_name"],
                                                   company_name=configuration["company_name"], ip=configuration["ip"],
                                                   server_port=configuration["anylog_server_port"],
                                                   hostname=configuration["hostname"],
                                                   external_ip=configuration["external_ip"],
                                                   rest_port=configuration["anylog_rest_port"], broker_port=broker_port,
                                                   proxy_ip=proxy_ip, cluster_id=cluster_id, location=location,
                                                   country=country, state=state, city=city)

        blockchain_store_policy(anylog_conn=anylog_conn, new_policy=new_policy, ledger_conn=configuration["ledger_conn"])
        policy = blockchain.get_policy(anylog_conn=anylog_conn, policy_type=node_type,
                                       where_conditions=where_conditions,
                                       bring_conditions="first", bring_values="[*][id]", separator=None,
                                       view_help=False)

    return policy

