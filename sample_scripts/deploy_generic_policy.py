import __init__
import anylog_api
import blockchain_cmd

def main():
    """
    The following is an example of adding an hierarchy of personalized policise to the AnyLog blockchain.
    :params:
        rest_conn:str - REST IP and PORT to connect to
        master_node:str - TCP master node information
        auth:tuple - REST authentication information
        timeout:int - REST timeout period
        policies:dict - dict of personalized policies
    """
    rest_conn='127.0.0.1:2049'
    master_node='127.0.0.1:2048'
    auth=None
    timeout=30

    # connect to AnyLog
    anylog_conn = anylog_api.AnyLogConnect(conn=rest_conn, auth=auth, timeout=timeout)

    # personalized hierarchy
    policies = {
        'manufacturer': { # layer 0
            'name': 'Ai-Op',
            'url': 'http://ai-op.com/'
        },
        'device': { # layer 1
            'name': 'fic',
            'manufacturer': ''
        },
        'sensor_type': { # layer 2
            'name': 'fic11',
            'device': ''
        },
        'sensor': { # layer 3
            'name': 'fic11',
            'sensor_type': ''
        },
        'sensor': { # layer 3
            'name': 'fic11_pv',
            'sensor_type': ''
        },
        'sensor': { # layer 3
            'name': 'fic11_mv',
            'sensor_type': ''
        }
    }

    """
    1. Check if policy exists if so keep ID info for next layer 
    2. If not - declare policy 
    2a. pull blockchain
    3. repeat step 1 
    """
    for policy in policies:
        blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=policy, exception=False)
        if len(blockchain) == 0:
            if policy == 'device':
                policies[policy]['manufacturer'] = id
            elif policy == 'sensor_type':
                policies[policy]['device'] = id
            elif policy == 'sensor':
                policies[policy]['sensor_type'] = id

            declare_generic_policy(conn=anylog_conn, policy_type=policy, policy_valus=policies[policy],
                                   master_node=master_node)
            # pull blockchain & re-query
            blockchain_cmd.pull_json(conn=anylog_conn, master_node=master_node, exception=False)
            if policy in ['manufacturer', 'device', 'sensor_type']:
                blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=policy, exception=False)

        if len(blockchain) != 0 and 'id' in blockchain and policy in blockchain[0][policy]:
            id = blockchain[0][policy][id]



if __name__ == '__main__':
    main()