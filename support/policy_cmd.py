import time

import __init__
import anylog_api
import blockchain_cmd
import create_declaration
import post_cmd

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
        node_id
    """
    run = 0
    policy_id = None
    while_conditions = []
    policy_type = list(new_policy)[0]
    for key in new_policy[policy_type]:
        value = new_policy[policy_type][key]
        if isinstance(value, str):
            value = value.replace('"', '').replace("'", "").lstrip().rstrip()
        stmt = '%s=%s'
        if isinstance(value, str) and (" " in value or "+" in value):
            stmt = '%s="%s"'
        while_conditions.append(stmt % (key, value))

    while run <= 10:
        # Pull from blockchain
        pull_status = blockchain_cmd.master_pull_json(conn=conn, master_node=master_node, exception=exception)
        if pull_status is True and master_node != 'local':
            # copy file
            post_cmd.copy_file(conn=conn, remote_node=master_node, remote_file='!!blockchain_file',
                               local_file='!blockchain_file', exception=exception)
        else:
            print('Faileed to pull from blockchain. Please double check master_node params in config. Current master: %s' % master_node)
            exit(1)
        if pull_status is True:
            blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=policy_type, where=while_conditions,
                                                       exception=exception)
        if len(blockchain) == 0: # add to blockchain
            blockchain_cmd.post_policy(conn=conn, policy=new_policy, master_node=master_node,
                                       exception=exception)
        if len(blockchain) == 1 and 'id' in blockchain[0][policy_type]: # extract policy id
            try:
                policy_id = blockchain[0][policy_type]['id']
            except Exception as e:
                pass
            else:
                run = 11
        else: # wait a few seconds between each iteration
            time.sleep(10)
        run += 1

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
        policy_name:str - from config extract policy_name
        new_policy:str - Policy to declare
    :retunr:
        policy_id - this can be used to verify policy and/or added to a consequent policy
    """
    run = 0
    policy_id = None

    if policy_type.lower() in ['master', 'operator', 'publisher', 'query']:
        new_policy = create_declaration.declare_node(config=config, location=location)
    elif policy_type.lower() == 'cluster':
        new_policy = create_declaration.declare_cluster(config=config)
    else:
        if exception is True:
            print('Invalid policy of type: %s' % policy_type)

    return declare_policy(conn=conn, master_node=master_node, new_policy=new_policy, exception=exception)


def drop_policy(conn:anylog_api.AnyLogConnect, master_node:str, policy_type:str, query_params:dict,
                exception:bool)->bool:
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
        value = query_params[key]
        if isinstance(value, str):
            value = value.replace('"', '').replace("'", "").lstrip().rstrip()
        stmt = '%s=%s'
        if isinstance(value, str) and (" " in value or "+" in value):
            stmt = '%s="%s"'
        while_conditions.append(stmt % (key, value))

    while run < 2 and status is True:
        pull_status = blockchain_cmd.master_pull_json(conn=conn, master_node=master_node, exception=exception)
        if pull_status is True and master_node != 'local':
            # copy file
            post_cmd.copy_file(conn=conn, remote_node=master_node, remote_file='!!blockchain_file',
                               local_file='!blockchain_file', exception=exception)
        if pull_status is True:
            blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=policy_type, where=while_conditions,
                                                       exception=exception)

        if run > 0 and len(blockchain) == 0: # if not first iteration validate policy was dropped
            pass
        elif len(blockchain) != 1: # if first iteration and len(blockchain) is 0 or greater than 1 there's an "issue" with the where
            status = False
        else: # drop policy if len(blockchain) == 1
            status = blockchain_cmd.drop_policy(conn=conn, policy=blockchain, master_node=master_node, exception=exception)
            time.sleep(10)
        run += 1
    return status
