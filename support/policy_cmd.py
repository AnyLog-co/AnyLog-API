import time

import __init__
import anylog_api
import blockchain_cmd
import create_declaration
import other_cmd

def declare_policy(conn:anylog_api.AnyLogConnect, master_node:str, new_policy:dict, exception:bool=False)->str:
    """
    Code to call corresponding blockchain in order to declare policy & return node ID
    :args:
        conn:anylog_api.AnyLogConnect - connction to AnyLog
        master_node:str - master node IP & Port
        new_policy:dict - policy to deploy
        exception:bool - whether to print exceptions
    :params:
        run:int - variable to use in while loop
        where_conditions:list - list of conditions to search by
        policy_id:str - ID of either existing or created policy
    :return:
        node_id - if unable to extract node id || fail to POST to blockchain return None (ie fails) 
    """
    policy_id = None
    where_conditions = []
    policy_type = list(new_policy)[0]
    print(new_policy)
    for key in new_policy[policy_type]:
        where_conditions.append(other_cmd.format_string(key, new_policy[policy_type][key]))

    # Get Policy ID as part of the prepare process
    policy_id = blockchain_cmd.prepare_policy(conn=conn, policy_type=policy_type, policy=new_policy, exception=exception)

    # check if policy already in ledger based on where_conditions
    where_conditions.append('id=%s' % policy_id)
    blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=policy_type, where_conditions=where_conditions,
                                  exception=exception)
    if len(blockchain) == 0:
        # Post policy to ledger
        if blockchain_cmd.post_policy(conn=conn, policy=new_policy, master_node=master_node, exception=exception):
            policy_id = None

        """
        # There's a bug with `blockchain wait` via rest, as such cannot validate blockchain has been updated until issue is fixed   
        if policy_id is not None:
            # sync & wait until blockchain is updated process
            blockchain_cmd.blockchain_sync(conn=conn, exception=exception)
            blockchain_cmd.blockchain_wait(conn=conn, policy_type=policy_type, where_conditions=while_conditions,
                                           exception=exception)
        """
    return policy_id

def declare_anylog_policy(conn:anylog_api.AnyLogConnect, policy_type:str, config:dict, master_node:str,
                          location:bool=False, exception:bool=False)->str:
    """
    Declare an AnyLog policy to blockchain
        - master
        - cluster
        - operator
        - publisher
        - query
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        policy_type:str - type of policy to declare
        master_node:str - IP & Port of master node, set to 'local' if running against master
        config:dict - configuration from file
        location:bool - whether to declare location in policy
        exception:bool - whether to print exceptions
    :params:
        new_policy:str - Policy to declare
    :return:
        policy_id - this can be used to verify policy and/or added to a consequent policy
    """
    if policy_type.lower() in ['master', 'operator', 'publisher', 'query']:
        new_policy = create_declaration.declare_node(config=config, location=location)
    elif policy_type.lower() == 'cluster':
        new_policy = create_declaration.declare_cluster(config=config)
    else:
        if exception is True:
            print('Invalid policy of type: %s' % policy_type)

    return declare_policy(conn=conn, master_node=master_node, new_policy=new_policy, exception=exception)


def drop_policy(conn:anylog_api.AnyLogConnect, master_node:str, policy_type:str, query_params:dict, exception:bool)->bool:
    """
    Drop policy based on type and a subset of parameters
    :args:
        conn:anylog_api.AnyLogConnect - connection  to AnyLog
        policy_type:str - type of policy to drop
        query_params:dict - A subset of key value pairs to locate policy by
        exception:bool - whether to write exception
    :params:
        status:bool
        where_conditions:list - list of conditions to search by
        blockchain:dict - extracted blockchain based on query_params
    """
    status = True
    run = 0
    while_conditions = []
    for key in query_params:
        while_conditions.append(other_cmd.format_string(key, query_params[key]))

    blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=policy_type, where_conditions=while_conditions,
                                               exception=exception)

    if len(blockchain) == 1:
        status = blockchain_cmd.drop_policy(conn=conn, policy=blockchain, master_node=master_node, exception=exception)
    elif exception is True:
        print('Failed to drop policy because `blockchain get` returned %s policies. Please update your query_params' % len(blockchain))
        status = False
        
    return status
