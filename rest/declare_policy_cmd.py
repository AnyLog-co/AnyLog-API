import time

import __init__
import anylog_api
import create_declaration
import blockchain_cmd


def declare_anylog_policy(conn:anylog_api.AnyLogConnect, policy_type:str, config:dict, location:bool=False,
                          exception:bool=False)->str:
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
        config:dict - configuration from file
        location:bool - whether to declare location in policy
        exception:bool - whether to print exceptions
    :params:
        run:int - variable to use in while loop
        policy_id:str - ID of either existing or created policy
        policy_name:str - from config extract policy_name
        new_policy:str - Policy to declare
    :retunr:
        policy_id - this can be used to verify policy and/or added to a consequent policy
    """
    run = 0
    policy_id = None

    if policy_type.lower() in ['master', 'operator', 'publisher', 'query']:
        new_policy = create_declaration.declare_node(config=config, location=location)
        policy_name = config['name']
    elif policy_type.lower() == 'cluster':
        new_policy = create_declaration.declare_cluster(config=config)
        policy_name = config['cluster_name']
    else:
        if exception is True:
            print('Invalid policy of type: %s' % policy_type)
        return policy_id

    while run <= 10:
        # Pull from blockchain
        if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception=exception):
            # check if in blockchain
            blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=policy_type,
                                                       where=['company="%s"' % config['company_name'],
                                                              'name=%s' % policy_name],
                                                       exception=exception)
        if len(blockchain) == 0: # add to blockchain
            blockchain_cmd.post_policy(conn=conn, policy=new_policy, master_node=config['master_node'],
                                       exception=exception)
        if len(blockchain) == 1 and 'id' in blockchain[0][policy_type]: # extract policy id
            try:
                policy_id = blockchain[0][policy_type]['id']
            except Exception as e:
                pass
            run = 11
        else: # wait a few seconds between each iteration
            time.sleep(10)
        run += 1

    return policy_id



