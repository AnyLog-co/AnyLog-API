import argparse
import json
import os

import anylog_connector
import blockchain
import support
import generic_get
import generic_post

import declare_policy
import master
import query

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]

def __check_license(anylog_conn:anylog_connector.AnyLogConnector):
    is_license = True
    license = generic_get.check_license(anylog_conn=anylog_conn, destination=None, execute_cmd=True, view_help=False)
    for section in ["License Type", "Licensed Company", "Expiration Date"]:
        if section not in license:
            is_license = False

    return is_license

def main():
    """
    Deploy an AnyLog node via REST
    :process:
        0. An AnyLog with TCP, REST and Broker (if set) should be running
        1. Validate node is accessible via REST
        3. Set license key
        4. prepare configuration
        5. set blockchain synchronizer
        6. deploy configuraton for a specific node type
    :positional arguments:
        rest_conn             REST connection information (example: {user}:{password}@
        config_file           Configuration file to be utilized
        license_key           AnyLog License Key
    :optional arguments:
        -h, --help                      show this help message and exit
        --timeout       TIMEOUT         REST timeout (default: 30)
        -e,--exception  [EXCEPTION]     Whether to print errors (default: False)
    :params:
        config_file:str - configuration file
        conn:str - REST connection IP and Port
        auth:tuple - REST authentication
        anylog_conn:anylog_connector.AnyLogConnector - Connection to AnyLog via REST
        configuration:dict - deployment configurations (both file and AnyLog dictionary)
    """
    config_file = os.path.join(ROOT_DIR, 'configurations', 'master_configs.env')
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn', type=support.validate_conn_pattern, default='127.0.0.1:2049', help='REST connection information')
    parser.add_argument('config_file', type=str, default=config_file, help='Configuration file to be utilized')
    parser.add_argument('license_key', type=str, default=None, help='AnyLog License Key')
    parser.add_argument('--policy-deployment', type=bool, nargs='?', const=True, default=False, help="Deploy node based on ")
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = parser.parse_args()

    scripts = []

    conn, auth = support.anylog_connection(rest_conn=args.rest_conn)
    anylog_conn = anylog_connector.AnyLogConnector(conn=conn, auth=auth, timeout=args.timeout, exception=args.exception)

    if generic_get.get_status(anylog_conn=anylog_conn, json_format=True) is False:
        print(f"Failed to connect to AnyLog via {conn}. Cannot Continue")
        exit(1)

    if __check_license(anylog_conn=anylog_conn) is False:
        generic_post.set_license_key(anylog_conn=anylog_conn, license_key=args.license_key)

    configuration = support.prepare_dictionary(anylog_conn=anylog_conn, config_file=args.config_file,
                                                          exception=args.exception)

    if len(configuration) == 0 or configuration is None:
        print(f"Failed to get configurations against file {args.config_file} and connection {conn}. Cannot continue")
        exit(1)

    if args.policy_deployment is True:
        scripts.append(generic_post.run_scheduler(anylog_conn=anylog_conn, schedule_number=1, execute_cmd=False,
                                                  view_help=False))
        scripts.append(blockchain.run_synchronizer(anylog_conn=anylog_conn, source=configuration['blockchain_source'],
                                                   time=configuration['sync_time'],
                                                   dest=configuration['blockchain_destination'],
                                                   connection=configuration['ledger_conn'], execute_cmd=False,
                                                   view_help=False))
    else:
        if generic_get.get_scheduler(anylog_conn=anylog_conn, schedule_number=1, view_help=False) is False:
            if generic_post.run_scheduler(anylog_conn=anylog_conn, schedule_number=1, view_help=False) is False:
                print("Failed to set schedule 1. Cannot  Continue")
                exit(1)

        if configuration['node_type'] not in ['rest', 'none']:
            if support.check_synchronizer(anylog_conn=anylog_conn) is False:
                if blockchain.run_synchronizer(anylog_conn=anylog_conn, source=configuration['blockchain_source'],
                                               time=configuration['sync_time'],
                                               dest=configuration ['blockchain_destination'],
                                               connection=configuration['ledger_conn'], view_help=False) is False:
                    print(f"Failed to declare blockchain sync against {conn}")

    if configuration['node_type'] in ['master', 'ledger', 'standalone', 'standalone-publisher']:
        declare_policy.declare_node(anylog_conn=anylog_conn, node_type="master", configuration=configuration,
                                    cluster_id=None, exception=args.exception)
        master.deploy_node(anylog_conn=anylog_conn, configuration=configuration, scripts=scripts,
                           policy_deployment=args.policy_deployment, exception=args.exception)
    # if configuration['node_type'] in ['operator', 'standalone']:
    #     declare_policy.declare_node(anylog_conn=anylog_conn, node_type="operator", configuration=configuration,
    #                                 cluster_id=None, exception=args.exception)
    # if configuration['node_type'] in ['publisher', 'standalone-publisher']:
    #     declare_policy.declare_node(anylog_conn=anylog_conn, node_type="publisher", configuration=configuration,
    #                                 cluster_id=None, exception=args.exception)
    # if configuration['node_type'] in ['query']:
    #     declare_policy.declare_node(anylog_conn=anylog_conn, node_type="query", configuration=configuration,
    #                                 cluster_id=None, exception=args.exception)
    #     query.deploy_node(anylog_conn=anylog_conn, configuration=configuration, scripts=scripts,
    #                       policy_deployment=args.policy_deployment, exception=args.exception)
    #
    print(generic_get.get_processes(anylog_conn=anylog_conn, json_format=False, view_help=False))


if __name__ == '__main__':
    main()