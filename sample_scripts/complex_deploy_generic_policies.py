import json
import time

import __init__
import anylog_api
import blockchain_cmd
POLICIES = {
    'manufacturer': {
        'name': 'Bosch',
        'url': 'https://www.bosch-sensortec.com/'
    },
    'device': {
        'name': 'fic',
        'manufacturer': ''
    },
    'sensor_type': {
        'name': 'fic11',
        'device': ''
    },
    'tag1': {
        'tag': {
            'name': 'fic11',
            'sensor_type': ''
        }
    },
    'tag2': {
        'tag': {
            'name': 'fic11_pv',
            'sensor_type': ''
        }
    },
    'tag3': {
        'tag': {
            'name': 'fic11_mv',
            'sensor_type': ''
        }
    }
}


def __validate_json_format(policy:dict)->bool:
    """
    Validate policy format - print error by default
    :args:
        policy:dict - policy to check
    :params:
        status:bool
    :return:
        if policy format is correct then return True, else return False
    """
    status = True
    if not isinstance(policy, dict):
        print("Invalid %s type for policy (sample policy: {policy_type: {'key': 'value'}}" % type(policy))
        status = False
    elif len(list(policy.keys())) != 1:
        print("Invalid policy format (sample policy: {policy_type: {'key': 'value'}}")
        status = False
    return status


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


def main(rest_conn:str, master_node:str='local', auth:tuple=None, timeout:int=30, exception:bool=False):
    """
    The following is intended to show how to deploy add/remove a set of policies, with the thought that each consecutive
    policy requires the ID of the previous one
    :sample process:
        1. connect to AnyLog
        2. validate policy format
        3. Update policy with the ID of the previous policy
        4. check if policy exists
        5. add policy if DNE
        6. extract policy ID 
    Repeat steps 2-6. For policies of type tag the required ID is that of sensor_type
    :args:
        rest_conn:str - REST IP:Port information
        master_node:str - master node IP & port, if working directly against master node use 'local'
        auth:tuple - REST authentication information
        timeout:int - REST timeout period
        exception:bool - whether to print exception
    :params:
        anylog_conn:anylog_api.AnyLogConnect - connection to AnyLog
        where_conditions:dict - whether conditions to check blockchain against
    """
    # connect to AnyLog
    anylog_conn = anylog_api.AnyLogConnect(conn=rest_conn, auth=auth, timeout=timeout)
    policy_id = {}

    for policy in POLICIES:
        where_conditions = []
        policy = {policy: POLICIES[policy]}
        if 'tag' in list(policy.keys())[0]:
            policy = POLICIES[list(policy.keys())[0]]

        # validate policy, if a policy files I stop
        if not __validate_json_format(policy=policy): #
            exit(1)
       
        # Update policy with the ID of the previous policy
        policy_type = list(policy.keys())[0]
        if policy_type == 'device':
            policy[policy_type]['manufacturer'] = policy['manufacturer']
        elif policy_type == 'sensor_type':
            policy[policy_type]['device'] = policy['device']
        elif policy_type == 'tag':
            policy[policy_type]['sensor_type'] = policy['sensor_type']
        
        # build WHERE condition for checking if policy exists
        for key in policy[policy_type]:
            if isinstance(policy[policy_type][key], str):
                where_conditions.append("%s='%s'" % (key, policy[policy_type][key]))
            else:
                where_conditions.append("%s=%s" % (key, policy[policy_type][key]))

        # check if policy exists
        # 1. Pull from blockchain
        # 2. check if policy exists
        # 3. POST policy to blockchain
        # 4. Repeat steps 1 & 2 until policy appears
        count = 0
        boolean = False
        while boolean is False or count > 10:
            if blockchain_cmd.pull_json(conn=anylog_conn, master_node=master_node, exception=exception): # Pull to JSON
                blockchain = blockchain_cmd.blockchain_get(conn=anylog_conn, policy_type=policy_type, where=where_conditions, exception=exception)
                if len(blockchain) == 0 and count == 0:
                    blockchain_cmd.post_policy(conn=anylog_conn, policy=policy_type     , master_node=master_node, exception=exception)
                    time.sleep(60)
                elif len(blockchain) > 0: # policy found in blockchain
                    boolean = True
                count += 1

        # Extract node ID - if policy doesn't appear print error and exit
        if count > 10 and len(blockchain) == 0:
            print('Failed to validate policy was added to blockchain')
            exit(1)
        elif len(blockchain) >= 1:
            policy_id[policy_type] = __extract_node_id(node_type=policy_type, blockchain=blockchain)

        print(policy)

if __name__ == '__main__':
    main(rest_conn='10.0.0.228:22849')
