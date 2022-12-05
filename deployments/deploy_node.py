import argparse
import dotenv
import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from anylog_connection import AnyLogConnection
import support
import generic_get_calls


def __set_configs(rest_conn:str, config_file:str, auth:str=None, timeout:int=30, exception:bool=False)->(AnyLogConnection, dict):
    """
    Prepare basic configurations to utilize with AnyLog API
    :args:
        rest_conn:str - REST connection information
        config_file;str - Configuration file to be utilized
        auth:str - Authentication information (comma separated) [ex. username,password]
        timeout:int - REST timeout
        exception:bool - Whether to print errors
    :params;
        config_file:str - full path of config file
        configs:dict - content from config file
        auth:tuple - authentication information (if any)
        anylog_conn:class.AnyLogConnection - init of AnyLogConnection class
        default_configs:dict - (default) configs from AnyLog
    :return:
        anylog_conn, configs
    """
    # read configs
    configs = support.read_configs(config_file=config_file, exception=exception)

    # Set authentication
    if auth is not None:
        auth = tuple(auth.split(','))

    # connect to AnyLog instance  (anylog_connection.AnyLogConnection)
    anylog_conn = AnyLogConnection(conn=rest_conn, auth=auth, timeout=timeout)

    # validate connections
    if generic_get_calls.get_status(anylog_conn=anylog_conn, exception=exception) is False:
        print(f'Failed to connect to node: {anylog_conn}. Cannot continue')
        exit(1)
    default_configs = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, exception=exception)
    if configs == {} and default_configs == {}:
        print(
            f'Failed to read configuration from both file ({config_file}) and the defaults via REST (Node Conn: {rest_conn})')
        exit(1)

    # merge configs in default_configs that are not found in configs
    for param in default_configs:
        upper_param = param.upper()
        if upper_param not in configs:
            configs[upper_param] = default_configs[param]

    # missing configs
    if 'HOSTNAME' not in configs:
        configs['HOSTNAME'] = generic_get_calls.get_hostname(anylog_conn=anylog_conn, exception=exception)

    for param in ['MEMBER', 'CLUSTER_NAME', 'LOCATION', 'COUNTRY', 'STATE', 'CITY']:
        if param not in configs:
            configs[param] = None

    if configs['NODE_TYPE'] == 'operator' and configs['CLUSTER_NAME'] is None:
        configs['CLUSTER_NAE'] = 'new-cluster'

    return anylog_conn, configs


def main():
    """
    The following deploys an AnyLog instance using REST. This deployment process requires the node to already be up
    running with at least TCP and REST communication up and running.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn', type=str, default='127.0.0.1:2049', help='REST connection information')
    parser.add_argument('config_file', type=str, default=os.path.join(ROOT_DIR, 'deployments/sample_configs.env'),
                        help='Configuration file to be utilized')
    parser.add_argument('--auth', type=str, default=None, help='Authentication information (comma separated) [ex. username,password]')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = parser.parse_args()

    config_file_path = os.path.expanduser(os.path.expandvars(args.config_file))
    if not os.path.isfile(config_file_path):
        print(f'Failed to locate file {args.config_file}')
        exit(1)
    anylog_conn, configs = __set_configs(rest_conn=args.rest_conn, config_file=config_file_path, auth=args.auth,
                                         timeout=args.timeout, exception=args.exception)

    if generic_get_calls.get_status(anylog_conn=anylog_conn, exception=args.exception) is False or anylog_conn is not AnyLogConnection:
        print(f'Failed to connect to AnyLog instance against {args.rest_conn}')


if __name__ == '__main__':
    main()