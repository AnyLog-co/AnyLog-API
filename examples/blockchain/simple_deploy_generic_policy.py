import argparse
import json

import __init__
import anylog_api
import errors

LOCATIONS = {
    'Los Angeles, CA': '33.8121, -117.91899',
    'San Francisco, CA': '37.786163522, -122.404498382',
    'Seattle, WA': '47.620182, -122.34933',
    'Philadelphia, PN': '39.949566, -75.15026',
    'Arlington, VA': '38.870983,  -77.05598',
    'Washington DC': '38.89773, -77.03653',
    'New York City, NY': '40.758595, -73.98447',
    'Orlando, FL': '28.37128, -81.51216',
    'Houston, TX': '29.97980499267578, -95.56627655029297',
    'Las Vegas': '36.1147, -115.1728'
}


def main():
    """
    The following is an example of adding a single policy to the AnyLog blockchain.
    The example is used by a client who's interested in knowing where their solar panels are located.
    :positional arguments:
        rest_conn             REST connection information
        master_node           TCP master information
    :optional arguments:
        -h, --help            show this help message and exit
        -a AUTH, --auth         AUTH      REST authentication information (default: None)
        -t TIMEOUT, --timeout   TIMEOUT   REST timeout period (default: 30)
    :params:
        polic}y:dict - new policy to be added into blockchain
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn',       type=str,   default='127.0.0.1:2049', help='REST connection information')
    parser.add_argument('master_node',     type=str,   default='127.0.0.1:2048', help='TCP master information')
    parser.add_argument('-a', '--auth',    type=tuple, default=None, help='REST authentication information')
    parser.add_argument('-t', '--timeout', type=int,   default=30,   help='REST timeout period')
    args = parser.parse_args()

    # connect to AnyLog
    anylog_conn = anylog_api.AnyLogConnect(conn=args.rest_conn, auth=args.auth, timeout=args.timeout)

    # personalized hierarchy
    policy = { 'panel': {
        'name': None,
        'city': None,
        'loc': None,
        'owner': 'AFG'
    }}

    for location in LOCATIONS:
        policy['panel']['name'] = 'Panel %s' % str(int(list(LOCATIONS).index(location)) + 1)
        policy['panel']['city'] = location
        policy['panel']['loc'] = LOCATIONS[location]
        send_policy = "<policy=%s>" % json.dumps(policy)

        # POST policy
        if blockchain_cmd.drop_policy(conn=anylog_conn, policy=policy, master_node=args.master_node,
                                      exception=True):
            print('Policy Added')
        else:
            print('Failed to add policy')

if __name__ == '__main__':
    main()