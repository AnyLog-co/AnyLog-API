import argparse
import os
import re

import blockchain_calls

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


def anylog_connection(rest_conn:str, timeout:int)->AnyLogConnector:
    """
    Connect to AnyLog node
    :args:
        rest_conn:str - REST connection information
        timeout:int - REST timeout
    :params:
        conn:str - REST IP:Port  from rest_conn
        auth:tuple - REST authentication from rest_conn
    :return:
        connection to AnyLog node
    """
    conn = rest_conn.split('@')[-1]
    auth = None
    if '@' in rest_conn:
        auth = tuple(rest_conn.split('@')[0].split(':'))

    return AnyLogConnector(conn=conn, auth=auth, timeout=timeout)


def set_license_key(anylog_conn:AnyLogConnector, license_key:str, exception:bool=False):
    """
    set license key
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        license_key:str - License key
        exception:bool - whether to print exceptions
    :params:
        count:int - counter
        is_license:bool - whether license exists or not
    """
    count = 0

    is_license = generic_get_calls.get_license(anylog_conn=anylog_conn, view_help=False, exception=exception)
    if is_license is False and (license_key is None or license_key == ''):
        print("License Key not provided, cannot continue setting up the node")
        exit(1)

    while is_license is False and count < 2:
        generic_post_calls.activate_license_key(anylog_conn=anylog_conn, license_key=license_key,
                                                exception=exception)
        is_license = generic_get_calls.get_license(anylog_conn=anylog_conn, view_help=False, exception=exception)
        count += 1

    if is_license is False:
            print(f"Failed to set AnyLog license with license: {license_key}")
            exit(1)
    else:
        print("AnyLog has been activated")


def set_synchronizer(anylog_conn:AnyLogConnector, configuration:dict, exception:bool):
    counter = 0
    blockchain_source = 'master'
    if 'blockchain_source' in configuration:
        blockchain_source = configuration['blockchain_source']
    blockchain_destination='file'
    if 'blockchain_destination' in configuration:
        blockchain_destination = configuration['blockchain_destination']
    sync_time='30 seconds'
    if 'sync_time' in configuration:
        sync_time = configuration['sync_time']
    ledger_conn = f"127.0.0,1:32048"
    if 'ledger_conn' in configuration:
        ledger_conn = configuration['ledger_conn']
    elif 'anylog_server_port' in configuration:
        ledger_conn=f"127.0.0.1:{configuration['anylog_server_port']}"

    processes = generic_get_calls.get_processes(anylog_conn=anylog_conn, json_format=True, view_help=False, exception=exception)
    while processes['Blockchain Sync']['Status'] == 'Not declared' and counter < 2:
        blockchain_calls.blockchain_sync(anylog_conn=anylog_conn, blockchain_source=blockchain_source,
                                         blockchain_destination=blockchain_destination, sync_time=sync_time,
                                         ledger_conn=ledger_conn, view_help=False, exception=exception)
        processes = generic_get_calls.get_processes(anylog_conn=anylog_conn, json_format=True, view_help=False,
                                                    exception=exception)
        counter += 1
    if processes['Blockchain Sync']['Status'] == 'Not declared':
        print(f"Failed to enable blockchain sync")


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

    anylog_conn = anylog_connection(rest_conn=args.rest_conn, timeout=args.timeout)

    configuration = read_configs(config_file=args.config_file, exception=args.exception)
    if configuration == {}:
        print(f"Failed to extract content configuration file (configuration file: {args.config_file}. Cannot continue...")
        exit(1)

    if not generic_get_calls.get_status(anylog_conn=anylog_conn, json_format=True, view_help=False, exception=args.exception):
        print(f"Failed to connect to node against {anylog_conn.conn}. Cannot continue...")
        exit(1)

    if 'license_key' in configuration:
        set_license_key(anylog_conn=anylog_conn, license_key=configuration['license_key'], exception=args.exception)
    else:
        set_license_key(anylog_conn=anylog_conn, license_key=args.license_key, exception=args.exception)


    if 'node_type' in configuration and configuration['node_type'] not in ['generic', 'rest']:
        set_synchronizer(anylog_conn=anylog_conn, configuration=configuration, exception=args.exception)
    # if 'node_type' in configuration and configuration['node_type'] in ['ledger', 'standalone', 'standalone-publisher']:
    #     deploy_master(anylog_conn=anylog_conn, configuration=configuration, exception=args.exception)
    # if 'node_type' in configuration and configuration['node_type'] in ['operator', 'standalone']:
    #     pass
    # if 'node_type' in configuration and configuration['node_type'] in ['publisher', 'standalone-publisher']:
    #     pass
    # if 'node_type' in configuration and configuration['node_type'] == 'query':
    #     pass

    print(generic_get_calls.get_processes(anylog_conn=anylog_conn, json_format=False, view_help=False, exception=args.exception))


if __name__ == '__main__':
    main()