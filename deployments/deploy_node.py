import argparse
import ast
import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from anylog_connection import AnyLogConnection
from deploy_dbms import deploy_dbms

import blockchain_calls as blockchain_calls
import generic_get_calls as generic_get_calls
import generic_post_calls as generic_post_calls
import support

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
    config_file = os.path.expanduser(os.path.expandvars(config_file))
    if not os.path.isfile(config_file):
        print(f'Failed to locate {args.config_file}. Unable to deploy node')
        exit(1)

    configs = support.read_configs(config_file=config_file, exception=exception)

    # Set authentication
    auth = None
    if auth is not None:
        auth = tuple(args.auth.split(','))

    # connect to AnyLog instance  (anylog_connection.AnyLogConnection)
    anylog_conn = AnyLogConnection(conn=rest_conn, auth=auth, timeout=timeout)
    

    default_configs = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, exception=exception)
    if configs == {} and default_configs == {}:
        print(f'Failed to read configuration from both file ({config_file}) and the defaults via REST (Node Conn: {rest_conn})')
        exit(1)

    # merge configs in default_configs that are not found in configs
    for param in default_configs:
        if param not in configs:
            configs[param] = default_configs[param]
    if 'hostname' not in configs:
        configs['hostname'] = generic_get_calls.get_hostname(anylog_conn=anylog_conn, exception=exception)

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


    anylog_conn, configs = __set_configs(rest_conn=args.rest_conn, config_file=args.config_file, auth=args.auth,
                                         timeout=args.timeout, exception=args.exception)

    # connect dbms
    db_name = None
    if 'DEFAULT_DBMS' in configs:
        db_name = configs['DEFAULT_DBMS']
    if configs['DB_TYPE'] == 'sqlite':
        deploy_dbms(anylog_conn=anylog_conn, node_type=configs['NODE_TYPE'], db_type=configs['DB_TYPE'], db_name=db_name,
                    host=None, port=None, user=None, passwd=None, system_query=configs['SYSTEM_QUERY'],
                    memory=configs['MEMORY'], exception=args.exception)
    else:
        deploy_dbms(anylog_conn=anylog_conn, node_type=configs['NODE_TYPE'], db_type=configs['DB_TYPE'], db_name=db_name,
                    host=configs['DB_IP'], port=configs['DB_PORT'], user=configs['DB_USER'], passwd=configs['DB_PASSWD'],
                    system_query=configs['SYSTEM_QUERY'], memory=configs['MEMORY'], exception=args.exception)

    # run scheduler
    generic_post_calls.schedule_task(anylog_conn=anylog_conn, name=1, exception=args.exception)

        




if __name__ == '__main__':
    main()