import argparse
import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'python_rest'))

from anylog_connector import AnyLogConnector
import file_io
import generic_get_calls
import support

import run_master

def __connect_anylog(conn:str, auth:str, timeout:int, exception:bool=False)->AnyLogConnector:
    """
    Connect to AnyLog REST interface
    :args:
        conn:str - REST connection info (IP and Port)
        auth:str - authentication information
        timeout:str - REST timeout
        exception:bool - whether to print exceptions
    :params:
        anylog_conn:AnyLogConnector - connection to AnyLog REST
    :return:
        if able to get status returns connection, else None
    """
    if auth is not None:
        auth = tuple(auth.split(','))
    anylog_conn = AnyLogConnector(conn=conn, auth=auth, timeout=timeout)

    if generic_get_calls.get_status(anylog_conn=anylog_conn, json_format=True, exception=exception) is False:
        anylog_conn = None

    return anylog_conn


def __read_configs(anylog_conn:AnyLogConnector, config_file:str, exception:bool=False)->dict:
    """
    Read configuration from file and AnyLog (dictionary) configs, then merge them into one
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        config_file:str - configuration file
        exception:bool - whether to print exceptions
    :params:
        anylog_configs:dict - merged configs
        file_configs:dict - configs form file
        anylog_dict:dict - default AnyLog configs
    :return:
        anylog_configs
    """
    file_configs = {}

    config_file = os.path.expanduser(os.path.expandvars(config_file))
    if os.path.isfile(config_file):
        file_configs = file_io.read_configs(config_file=config_file, exception=exception)
    else:
        print(f'Notice: Failed to locate configuration file {config_file}')

    anylog_dict = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, json_format=True, exception=exception)

    anylog_configs = support.dictionary_merge(file_config=file_configs, anylog_config=anylog_dict, exception=exception)

    return anylog_configs


def __enable_mqtt(anylog_conn:AnyLogConnector, anylog_configs:dict, exception:bool)->bool:
    """
    Check if MQTT exists if not connect it
    """
    pass


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
        --auth              AUTH            Authentication information (comma separated) [ex. username,password] (default: None)
        --timeout           TIMEOUT         REST timeout (default: 30)
        -e, --exception     [EXCEPTION]     Whether to print errors (default: False)
    :params:
        config_file_path:str - full path of config_file
        anylog_conn:AnyLogConnection - connection to AnyLog node
        configs:str - configuration file
    """
    config_file=os.path.join(ROOT_DIR, 'deployments/sample_configs.env')
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn', type=str, default='127.0.0.1:2049', help='REST connection information')
    parser.add_argument('config_file', type=str, default=config_file, help='Configuration file to be utilized')
    parser.add_argument('--auth', type=str, default=None, help='Authentication information (comma separated) [ex. username,password]')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = parser.parse_args()

    anylog_conn = __connect_anylog(conn=args.rest_conn, auth=args.auth, timeout=args.timeout, exception=args.exception)
    if anylog_conn is None:
        print(f'Failed to connect to AnyLog node {args.rest_conn}. Cannot continue')
        exit(1)

    anylog_configs = __read_configs(anylog_conn=anylog_conn, config_file=args.config_file, exception=args.exception)


    if anylog_configs['node_type'] in ['ledger', 'standalone', 'standalone-publisher']:
        run_master.main(anylog_conn=anylog_conn, anylog_configs=anylog_configs, exception=args.exception)
    if anylog_configs['node_type'] in ['operator', 'standalone']:
        pass
    if anylog_configs['node_type'] in ['publisher', 'standalone-publisher']:
        pass
    if anylog_configs['node_type'] in ['query']:
        pass






if __name__ == '__main__':
    main()