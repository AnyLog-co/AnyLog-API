import argparse
import ast
import os
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).split('deployment_scripts')[0]
REST_PATH = os.path.join(ROOT_PATH, 'REST')
sys.path.insert(0, REST_PATH)

from anylog_connection import AnyLogConnection
import blockchain_calls
import generic_get_calls


def main():
    """
    Create an ANMP for a given policy based on given parameters
    :url:
    
    :positional arguments:
        conn                  REST IP/Port connection to work against
    :optional arguments:
        -h, --help                              show this help message and exit
        --policy-type       POLICY_TYPE         blockchain type that needs to be updated
        --where-conditions  WHERE_CONDITIONS    condition to find relevant policy
        --new-values        NEW_VALUES          comma separated list of values to update
        --master-node       MASTER_NODE         master node TCP connection information
        --auth              AUTH                Authentication (user, passwd) for node
        --timeout           TIMEOUT             REST timeout
        --exception         [EXCEPTION]         whether to print exception
    :params:
        anylog_conn:anylog_connection.AnyLogConnection - connection to AnyLog via REST
        policy_id:str - policy ID based on blockchain get
        new_policy:dict - ANMP policy to add
    :sample policy:
    {
        "anmp": {
            "48d5c6e224a92ee04756040128f6331f": {
                "ip": "127.0.0.1",
                "port": 2148
            }
        }
    }
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('conn', type=str, default='127.0.0.1:2049', help='REST IP/Port connection to work against')
    parser.add_argument('--policy-type', type=str, default='operator', help='blockchain type that needs to be updated')
    parser.add_argument('--where-conditions', type=str, default='name=!node_name and company=!company_name', help='condition to find relevant policy')
    parser.add_argument('--new-values', type=str, default='ip=127.0.0.1,hostname=new-host', help='comma separated list of values to update')
    parser.add_argument('--master-node', type=str, default='127.0.0.1:2048', help='master node TCP connection information')
    parser.add_argument('--auth', type=tuple, default=(), help='Authentication (user, passwd) for node')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('--exception', type=bool, nargs='?', const=True, default=False, help='whether to print exception')
    args = parser.parse_args()

    anylog_conn = AnyLogConnection(conn='10.0.0.111:2049', auth=args.auth, timeout=args.timeout)
    if not generic_get_calls.validate_status(anylog_conn=anylog_conn, exception=args.exception):
        print(f'Failed to validate connection to AnyLog on {anylog_conn.conn}')
        exit(1)

    policy_id = blockchain_calls.blockchain_get(anylog_conn=anylog_conn, policy_type=args.policy_type,
                                                where_condition=args.where_conditions,
                                                exception=args.exception)[0][args.policy_type]['id']
    new_policy = {policy_id: {}}
    for param in args.new_values.split(','):
        key = param.split('=')[0].rstrip().lstrip()
        value = param.split('=')[-1].rstrip().lstrip()
        new_policy[policy_id][key] = value

    blockchain_calls.declare_policy(anylog_conn=anylog_conn, policy={"anmp": new_policy},
                                    master_node=args.master_node, exception=args.exception)


if  __name__ == '__main__':
    main()