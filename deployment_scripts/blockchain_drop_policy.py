import argparse
import os
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).split('deployment_scripts')[0]
REST_PATH = os.path.join(ROOT_PATH, 'REST')
sys.path.insert(0, REST_PATH)

from anylog_connection import AnyLogConnection
import authentication
import blockchain_calls
import database_calls
import deployment_calls
import generic_get_calls
import generic_post_calls


def main():
    """
    Example for drop policy
    :positional arguments:
          conn                  Node to execute against
    :optional arguments:
          -h, --help                    show this help message and exit
          --auth        AUTH            Authentication (user, passwd) for node
          --timeout     TIMEOUT         REST timeout
          --exception   EXCEPTION       whether to print exception
    :params:
        anylog_conn:AnyLogConnection - Connection to AnyLog node
        policy:dict - Policy to drop
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('conn', type=str, default='127.0.0.1:2149', help='Node to execute against')
    parser.add_argument('--auth', type=tuple, default=(), help='Authentication (user, passwd) for node')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('--exception', type=bool, nargs='?', const=True, default=False, help='whether to print exception')
    args = parser.parse_args()

    anylog_conn = AnyLogConnection(conn=args.conn, auth=args.auth, timeout=args.timeout)


    policy = blockchain_calls.blockchain_get(anylog_conn=anylog_conn, policy_type='operator',
                                           where_condition="name=!node_name and company=!company_name and ip=!external_ip and port=!anylog_server_port",
                                           bring_condition=None, separator=None, exception=args.exception)

    if drop_policy(anylog_conn=anylog_conn, policy=policy, exception=args.exception) is False:
        print('Failed to drop policy')


if __name__ == '__main__':
    main()