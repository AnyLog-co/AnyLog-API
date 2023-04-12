import argparse
import os


ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]

import master

import generic_get_calls
import deployment_support



def main():
    """
    The following deploys an AnyLog instance using REST. This deployment process requires the node to already be up
    running with at least TCP and REST communication.
    :process:
        1. connect to AnyLog + get params
        2. connect to database
        3. run scheduler / blockchain sync
        4. declare policies
        5. set partitions (operator only)
        6. buffer & streaming
        7. publisher / operator `run` process
    :positional arguments:
        rest_conn             REST connection information
        config_file           Configuration file to be utilized
    :optional arguments:
        -h, --help                          show this help message and exit
        --timeout           TIMEOUT         REST timeout (default: 30)
        -e, --exception     [EXCEPTION]     Whether to print errors (default: False)
    :params:
        config_file_path:str - full path of config_file
        anylog_conn:AnyLogConnection - connection to AnyLog node
        configs:str - configuration file
    """
    config_file=os.path.join(ROOT_DIR, 'configurations', 'master_configs.env')
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn', type=deployment_support.validate_conn_pattern, default='127.0.0.1:2049', help='REST connection information')
    parser.add_argument('config_file', type=str, default=config_file, help='Configuration file to be utilized')
    parser.add_argument('license_key', type=str, default=None, help='AnyLog License Key')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = parser.parse_args()

    anylog_conn = deployment_support.anylog_connection(rest_conn=args.rest_conn, timeout=args.timeout)
    if not generic_get_calls.get_status(anylog_conn=anylog_conn, json_format=True, view_help=False, exception=args.exception):
        print(f"Failed to connect to node against {anylog_conn.conn}. Cannot continue...")
        exit(1)

    deployment_support.set_license_key(anylog_conn=anylog_conn, license_key=args.license_key, exception=args.exception)

    configuration = deployment_support.set_dictionary(anylog_conn=anylog_conn, config_file=args.config_file, exception=args.exception)
    if configuration == {}:
        print(f"Failed to extract content configuration file (configuration file: {args.config_file}. Cannot continue...")
        exit(1)

    if 'node_type' in configuration and configuration['node_type'] not in ['generic', 'rest']:
        deployment_support.set_synchronizer(anylog_conn=anylog_conn, configuration=configuration, exception=args.exception)
    if 'node_type' in configuration and configuration['node_type'] in ['ledger', 'master', 'standalone', 'standalone-publisher']:
        master.deploy_node(anylog_conn=anylog_conn, configuration=configuration, exception=args.exception)

    print(generic_get_calls.get_processes(anylog_conn=anylog_conn, json_format=False, view_help=False, exception=args.exception))


if __name__ == '__main__':
    main()