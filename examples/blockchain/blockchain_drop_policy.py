import argparse
import json

import __init__
import anylog_api
import blockchain_cmd
import errors

LOCATIONS = [
    'Los Angeles, CA',
    'San Francisco, CA',
    'Seattle, WA',
    'Philadelphia, PN',
    'Arlington, VA',
    'Washington DC',
    'New York City, NY',
    'Orlando, FL',
    'Houston, TX',
    'Las Vegas'
]


def main():
    """
    The following is an example of removing a policy from the AnyLog blockchain this process can only be used with
        master node.
    The example is based on he policies that are created in simple_deploy_generic_policy
    :positional arguments:
        rest_conn             REST connection information
        master_node           TCP master information
    :optional arguments:
        -h, --help            show this help message and exit
        -a AUTH, --auth         AUTH      REST authentication information (default: None)
        -t TIMEOUT, --timeout   TIMEOUT   REST timeout period (default: 30)
    :params:

    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn',       type=str,   default='127.0.0.1:2049', help='REST connection information')
    parser.add_argument('master_node',     type=str,   default='127.0.0.1:2048', help='TCP master information')
    parser.add_argument('-a', '--auth',    type=tuple, default=None, help='REST authentication information')
    parser.add_argument('-t', '--timeout', type=int,   default=30,   help='REST timeout period')
    args = parser.parse_args()

    # connect to AnyLog
    anylog_conn = anylog_api.AnyLogConnect(conn=args.rest_conn, auth=args.auth, timeout=args.timeout)

    # Pull latest blockchain
    if blockchain_cmd.pull_json(conn=anylog_conn, master_node=args.master_node, exception=True):
        for city in LOCATIONS:
            # get value(s) from blockchain
            where_condition = ['city="%s"' % city]
            blockchain = blockchain_cmd.blockchain_get(conn=anylog_conn, policy_type="panel",
                                                       where=where_condition, exception=True)

            if len(blockchain) == 1:
                policy = blockchain[0]
                # Drop policy, when an error is returned the code
                if blockchain_cmd.drop_policy(conn=anylog_conn, policy=policy, master_node=args.master_node,
                                              exception=True):
                    print('Policy with ID %s was dropped' % blockchain[0]['panel']['id'])
                else:
                    print('Policy with ID %s was not dropped' % blockchain[0]['panel']['id'])
            else:
                print(('With the given where condition(s) {%s} either no policies were returned or more than one policy'
                     +' returned. As such wil not remove from blockchain.\nPlease update WHERE condition.') % where_condition)


if __name__ == '__main__':
    main()