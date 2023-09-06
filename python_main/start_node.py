"""
1. get information from configuration file
"""
import argparse
import os
import utils_file_io

import generic
import anylog_api_py.support as support
from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.generic_get_cmd import get_status
from anylog_api_py.generic_post_cmd import declare_anylog_path, create_work_directory




ROOT_PATH = os.path.expanduser(os.path.expandvars('$HOME'))
# configuration file is based on https://github.com/AnyLog-co/deployments/blob/master/docker-compose/anylog-generic/anylog_configs.env
CONFIG_FILE = os.path.expanduser(os.path.expandvars(os.path.join(ROOT_PATH, 'deployments', 'docker-compose', 'anylog-generic', 'anylog_configs.env')))


def main():
    """
    deployment script, but in (python) REST API format
    :process:
        1. extract connection information and validate connectivity
        2. set env configurations
        3.set anylog_path and create work directories
    :positional arguments:
        conn:str                  REST credentials for the node to communicate with
        config_file               configuration file to utilize for deploying an AnyLog node
    :optional arguments:
        -h, --help                      show this help message and exit
        --timeout       [TIMEOUT]       REST timeout
        --exception     [EXCEPTION]     whether to print exceptions or not
    :params:
        conn:str - IP and port
        auth:tuple -  credentials
        anylog_connector:AnyLogConnector - connection to AnyLog node
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('conn', type=support.check_conn_format, default='127.0.0.1:32549', help='REST credentials for the node to communicate with')
    parser.add_argument('config_file', type=utils_file_io.check_file, default=CONFIG_FILE, help='configuration file to utilize for deploying an AnyLog node')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('--exception', type=bool, nargs='?', const=True, default=False, help='whether to print exceptions or not')
    args = parser.parse_args()

    # extract connection information and validate connectivity
    conn, auth = support.extract_conn_information(conn_ip_port=args.conn)
    anylog_connector = AnyLogConnector(conn=conn, auth=auth, timeout=args.timeout)
    if get_status(anylog_conn=anylog_connector, exception=args.exception) is False:
        print(f"Failed to connect to node {conn}, cannot continue...")
        exit(1)

    # get dictionary information
    anylog_configs = generic.set_params(anylog_connector=anylog_connector, config_file=args.config_file, exception=args.exception)

    if not declare_anylog_path(anylog_conn=anylog_connector, anylog_path=anylog_configs['anylog_path'], exception=args.exception):
        print("Failed to declare Anylog path, cannot continue...")
        exit(1)
    if not create_work_directory(anylog_conn=anylog_connector, exception=args.exception):
        print(f"Failed to create work directories within {anylog_configs['anylog_path']}")
        exit(1)






if __name__ == '__main__':
    main()








