import time

import __init__
import anylog_api
import create_declaration
import blockchain_cmd


def __extract_node_id(node_type:str, blockchain:dict)->str:
    """
    Extract node ID from blockchain
    :args:
        node_type:str - node type to extract ID 
        blockchain:dict - pulled blockchain
    :params:
        node_id:str - ID of node
    """
    node_id = None
    if 'id' in blockchain[0][node_type]:
        try:
            node_id = blockchain[0][node_type]['id']
        except Exception as e:
            pass

    return node_id


def declare_cluster(conn:anylog_api.AnyLogConnect, config:dict, exception:bool=False)->str:
    """
    Declare cluster policy
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        config:dict - configuration from file
        location:bool - whwether to declare location in policy
        exception:bool - whether to print exceptions
    :params:
        status:bool
        cluster_id:str - ID of either existing or created cluster
        new_policy:str - Policy to declare
    :retunr:
        cluster_id
    """
    cluster_id = None
    new_policy = create_declaration.declare_cluster(config=config)
    
    # declare cluster if DNE 
    if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception=exception):
        blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type='cluster',
                                                   where=['company="%s"' % config['company_name'],
                                                          'name=%s' % config['cluster_name']],
                                                   exception=exception)
        if len(blockchain) == 0:
            blockchain_cmd.post_policy(conn=conn, policy=new_policy, master_node=config['master_node'],
                                       exception=exception)

    # extract cluster ID
    if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception=exception):
        blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type='cluster',
                                                   where=['company="%s"' % config['company_name'],
                                                          'name=%s' % config['cluster_name']],
                                                   exception=exception)
        if len(blockchain) >= 1:
            cluster_id = __extract_node_id( node_type='cluster', blockchain=blockchain)
    
    return cluster_id


def declare_node(conn:anylog_api.AnyLogConnect, config:dict, location:bool, exception:bool=False)->bool:
    """
    Declare node policy
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        config:dict - configuration from file
        location:bool - whwether to declare location in policy
        exception:bool - whether to print exceptions
    :params:
        status:bool
        new_policy:dict - Policy to declare
    :return:
        status
    """
    status = True
    new_policy = create_declaration.declare_node(config=config, location=location)
    blockchain = {}
    if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception=exception):
        blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=config['node_type'],
                                                   where=['ip=%s' % config['external_ip'],
                                                          'port=%s' % config['anylog_tcp_port']],
                                                   exception=exception)
        if len(blockchain) == 0:
            blockchain_cmd.post_policy(conn=conn, policy=new_policy, master_node=config['master_node'],
                                       exception=exception)

    if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception=exception) and len(blockchain) == 0:
        blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=config['node_type'],
                                                   where=['ip=%s' % config['external_ip'],
                                                          'port=%s' % config['anylog_tcp_port']],
                                                   exception=exception)

        if len(blockchain) == 0:
            status = False

    return status


def declare_generic_policy(conn:anylog_api.AnyLogConnect, master_node:str, policy_type:str,
                           policy_values:str, location:bool=False, extract_id:bool=True, exception:bool=False)->str:
    """
    Declare a personalized policy such as 'sensor' and 'device'
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        master_node:str - IP & Port of master node
        policy_type:str - the type of policy (ex. 'sensor' and 'device') 
        policy_values:dict - keey-value pairs correlated to device (ex. name, comapny, IP)
        location:bool - for devices and senors -- add a location (lat and long) of the new policy.
                        If set to (True), the location will be the same as that of the node from which the policy 
                        was declared. [(]Sample hard-coded location:  "37.5072,-122.2605"]
        extract_id:bool - Extract policy ID
        exception:bool - whether to print exception
    :params:
        node_id:str - ID of node
        new_policy:dict - formatted new policy
    :return:
        node_id
            - If extract_id is True and able to extract ID then return ID
            - If able to add policy but no need for ID, return None
            - If fails returns False
    """
    node_id = None
    new_policy = create_declaration.declare_generic_policy(policy_type=policy_type, policy_values=policy_values,
                                                           location=location)

    where_conditions = []
    for param in new_policy[policy_type]:
        if isinstance(new_policy[policy_type][param], str):
            where_conditions.append('%s="%s"' % (param, new_policy[policy_type][param]))
        else:
            where_conditions.append('%s=%s' % (param, new_policy[policy_type][param]))

    # Post ppolicy
    if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception=exception):
        blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=policy_type, where=where_conditions,
                                                   exception=exception)
        if len(blockchain) == 0:
            status = blockchain_cmd.post_policy(conn=conn, policy=new_policy, master_node=master_node,
                                       exception=exception)
            if status is False:
                node_id = False
            time.sleep(60)

    # Extract ID
    if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception=exception) and extract_id is True and node_id is None:
        blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=policy_type, where=where_conditions,
                                                   exception=exception)

        if len(blockchain) >= 1:
            node_id = __extract_node_id(node_type=policy_type, blockchain=blockchain)
        else:
            node_id = False

    return node_id

