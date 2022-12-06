import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from anylog_connection import AnyLogConnection
import support
import generic_get_calls

def __read_configs(config_file:str, exception:bool=False)->dict:
    config_file = os.path.expanduser(os.path.expandvars(config_file))
    configs = support.read_configs(config_file=config_file, exception=exception)
    return configs


def __connect_anylog(rest_conn:str, auth:str=None, timeout:int=30, exception:bool=False)->AnyLogConnection:
    if auth is not None and not isinstance(auth, tuple):
        auth = tuple(auth.split(','))

    anylog_conn = AnyLogConnection(conn=rest_conn, auth=auth, timeout=timeout)
    if generic_get_calls.get_status(anylog_conn=anylog_conn, exception=exception) is False:
        print(f'Failed to connect to node: {anylog_conn}. Cannot continue')
        exit(1)
    return anylog_conn


def __format_configs(anylog_conn:AnyLogConnection, config_file:str, exception:bool=False)->dict:
    configs = {}
    env_configs = __read_configs(config_file=config_file, exception=exception)
    default_configs = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, exception=exception)
    if env_configs == {} and default_configs == {}:
        return configs
    if env_configs != {}:
        for param in env_configs:
            configs[param] = env_configs[param]

    elif default_configs != {}:
        for param in default_configs:
            if param not in env_configs:
                configs[param.upper()] = default_configs[param]

    if 'HOSTNAME' not in configs:
        configs['HOSTNAME'] = generic_get_calls.get_hostname(anylog_conn=anylog_conn, exception=exception)

    for param in ['MEMBER', 'CLUSTER_NAME', 'LOCATION', 'COUNTRY', 'STATE', 'CITY']:
        if param not in configs:
            configs[param] = None

    if configs['NODE_TYPE'] == 'operator' and configs['CLUSTER_NAME'] is None:
        configs['CLUSTER_NAE'] = 'new-cluster'

    if 'DB_TYPE' not in configs:
        configs['DB_TYPE'] = 'sqlite'
    if 'NOSQL_ENABLE' not in configs:
        configs['NOSQL_ENABLE'] = False
    for param in ['MEMORY', 'SYSTEM_QUERY']:
        if param not in configs:
            configs[param] = False
    for param in ['DEFAULT_DBMS', 'DB_IP', 'DB_PORT', 'DB_USER', 'DB_PASSWD']:
        if param not in configs:
            configs[param] = None

    for param in ['NOSQL_IP', 'NOSQL_PORT', 'NOSQL_USER', 'NOSQL_PASSWD']:
        if param not in configs:
            configs[param] = None

    return configs


def config_node(rest_conn:str, config_file:str, auth:str=None, timeout:int=30, exception:bool=False)->(AnyLogConnection, dict):
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
    # connect to AnyLog instance  (anylog_connection.AnyLogConnection)
    anylog_conn = __connect_anylog(rest_conn=rest_conn, auth=auth, timeout=timeout, exception=exception)

    # read configs & update with missing configs
    configs = __format_configs(anylog_conn=anylog_conn, config_file=config_file, exception=exception)

    return anylog_conn, configs
