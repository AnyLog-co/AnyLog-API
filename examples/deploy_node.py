import argparse
import json

from anylog_api.anylog_api import AnyLogAPI
import anylog_api.__support__ as anylog_api_support
import __support__ as support

import examples.declare_node as declare_node

def main():
    """
    :positional arguments:
        conn                  REST connection information (Format:  {user}:{password}@{ip}{port})
    :optional arguments:
        -h, --help            show this help message and exit
        --configs       CONFIGS         comma seperated dotenv configuration file(s)
        --timeout       TIMEOUT         REST timeout
        --edgelake      [EDGELAKE]      Connect to EdgeLake instance
        --exception     [EXCEPTION]     Print exception
        --license-key   LICENSE_KEY     License key fo AnyLog if not part of configs
    :params:
        conn:str - connection information for node
        node_status:bool - node status (True / False)
        params:dict - dictionary with configuration file(s) information
        dictionary_params:dict - merged configurations for both AnyLog/EdgeLake and configuration file
        generic_policy:dict - generated node policy
        policy_id:str - policy ID
    """
    parse = argparse.ArgumentParser()
    parse.add_argument("conn", type=anylog_api_support.validate_conn_info, default='127.0.0.1:32549', help='REST connection information (Format: {user}:{password}@{ip}{port})')
    parse.add_argument('--configs', type=support.check_configs, default=None, help='comma seperated dotenv configuration file(s)')
    parse.add_argument('--timeout', type=float, default=60, help='REST timeout')
    parse.add_argument('--edgelake',  type=bool, const=True, nargs='?', default=False, help='Connect to EdgeLake instance')
    parse.add_argument('--exception', type=bool, const=True, nargs='?', default=False, help='Print exception')
    parse.add_argument('--license-key', type=str, default=None, help='License key fo AnyLog if not part of configs')
    args = parse.parse_args()

    # can only use 1 connection at aa times
    conn = list(args.conn.keys())[0]
    if len(list(args.conn.keys())) != 1:
        for key in args.conn:
            if key != len(list(args.conn.keys())):
                del args.conn[key]

    # validate node is accessible
    args.conn[conn] = AnyLogAPI(conn=conn, timeout=args.timeout, exception=args.exception)
    node_status = args.conn[conn].get_status(destination=None, view_help=False)
    if node_status is False:
        raise ConnectionError(f'Failed to connect to node against {conn}')

    # read file & update AnyLog dictionary
    for config_file in args.configs:
        params = support.read_configs(config_file=config_file, exception=args.exception)
        args.conn[conn].execute_post(command='params', payload=params, destination=None, view_help=False)
    dictionary_params = args.conn[conn].execute_get(command="get dictionary where format=json", destination=None,
                                                    view_help=False)
    dictionary_params = anylog_api_support.format_data(data=dictionary_params)

    # if fails will execute a raise exception
    anylog_api_support.validate_params(params=list(dictionary_params.keys()), is_edgelake=args.edgelake)

    generic_policy = declare_node.generic_node(params=dictionary_params)
    generic_policy[dictionary_params['node_type']]['script'] = declare_node.create_scripts(params=dictionary_params)

    policy_id = None
    status = False
    while not policy_id:
        policy_id = declare_node.check_policy(conn=args.conn[conn], policy_type=dictionary_params['node_type'], policy_name=generic_policy[dictionary_params['node_type']]['name'])
        if not policy_id and status is False:
            declare_node.declare_policy(conn=args.conn[conn], policy=generic_policy, ledger_conn=dictionary_params['ledger_conn'])
            status = True
        elif status is True and not policy_id:
            raise ConnectionError(f'Failed to publish policy against {conn}')
        else:
            declare_node.config_policy(conn=args.conn[conn], policy_id=policy_id)

    output = args.conn[conn].execute_get(command='get processes', destination=None, view_help=False)
    print(output)


if __name__ == '__main__':
    main()


