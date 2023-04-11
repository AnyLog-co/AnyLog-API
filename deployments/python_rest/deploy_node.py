import argparse
import os
import re

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]

from anylog_connector import AnyLogConnector
import generic_get_calls
import generic_post_calls

from file_io import read_configs
from master import deploy_master

def validate_conn_pattern(conn:str)->str:
    """
    Validate connection information format is connect
    :valid formats:
        127.0.0.1:32049
        user:passwd@127.0.0.1:32049
    :args:
        conn:str - REST connection information
    :params:
        pattern1:str - compiled pattern 1 (127.0.0.1:32049)
        pattern2:str - compiled pattern 2 (user:passwd@127.0.0.1:32049)
    :return:
        if fails raises Error
        if success returns conn
    """
    pattern1 = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$')
    pattern2 = re.compile(r'^\w+:\w+@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$')

    if not pattern1.match(conn) and not pattern2.match(conn):
        raise argparse.ArgumentTypeError(f'Invalid REST connection format: {conn}')

    return conn


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
    parser.add_argument('rest_conn', type=validate_conn_pattern, default='127.0.0.1:2049', help='REST connection information')
    parser.add_argument('config_file', type=str, default=config_file, help='Configuration file to be utilized')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('--license-key', type=str, default=None, help='AnyLog License Key')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = parser.parse_args()

    conn = args.rest_conn.split('@')[-1]
    auth = None
    if '@' in args.rest_conn:
        auth = tuple(args.rest_conn.split('@')[0].split(':'))
    anylog_conn = AnyLogConnector(conn=conn, auth=auth, timeout=args.timeout)

    configuration = read_configs(config_file=args.config_file, exception=args.exception)
    if configuration == {}:
        print(f"Failed to extract content configuration file (configuration file: {args.config_file}, cannot continue...")
        exit(1)
    if not generic_get_calls.get_status(anylog_conn=anylog_conn, json_format=True, view_help=False, exception=args.exception):
        print(f"Failed to connect to node against {conn}. Cannot Continue...")
        exit(1)
    if 'LICENSE_KEY' not in configuration and args.license_key is None:
        print(f"Unable to locate license key, Cannot continue...")
        exit(1)
    else:
        license_key = args.license_key
        if 'LICENSE_KEY' in configuration:
            license_key = configuration['LICENSE_KEY']
        count = 0
        is_license = generic_get_calls.get_license(anylog_conn=anylog_conn, view_help=False, exception=args.exception)
        while is_license is False and count < 2:
            generic_post_calls.activate_license_key(anylog_conn=anylog_conn, license_key=license_key, exception=args.exception)
            is_license = generic_get_calls.get_license(anylog_conn=anylog_conn, view_help=False, exception=args.exception)
            count += 1
        if is_license is False:
            print(f"Failed to set AnyLog license with license: {license_key}")
            exit(1)
        else:
            print("AnyLog has been activated")

    if 'NODE_TYPE' in configuration and configuration['NODE_TYPE'] in ['master', 'standalone', 'standalone-publisher']:
        deploy_master(anylog_conn=anylog_conn, configuration=configuration, exception=args.exception)
    if 'NODE_TYPE' in configuration and configuration['NODE_TYPE'] in ['operator', 'standalone']:
        pass
    if 'NODE_TYPE' in configuration and configuration['NODE_TYPE'] in ['publisher', 'standalone-publisher']:
        pass
    if 'NODE_TYPE' in configuration and configuration['NODE_TYPE'] == 'query':
        pass

    print(generic_get_calls.get_processes(anylog_conn=anylog_conn, json_format=False, view_help=False, exception=args.exception))


if __name__ == '__main__':
    main()