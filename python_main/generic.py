import os

from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.generic_get_calls import get_dictionary
from anylog_api_py.generic_post_calls import set_anylog_home, create_directories

from file_io import read_configs

ROOT_DIR = os.path.expanduser(os.path.expandvars(__file__)).split('python_main')[0]


def __merge_configs(file_configs:dict, anylog_configs:dict)->dict:
    """
    Merge file and internal configurations into a single dictionary
    :args:
        file_configs:dict - configuration from file
        anylog_configs:dict - configuration from within the node
    :params:
        node_configs:dict - combined configurations
    :return:
        node_configs
    """
    node_configs = {}
    for config in anylog_configs:
        if config.lower() in ['internal_ip', 'local_ip', 'ip']:
            node_configs['ip'] = anylog_configs[config]
        else:
            node_configs[config.lower()] = anylog_configs[config]

    for config in file_configs:
        if config.lower() in ['internal_ip', 'local_ip', 'ip']:
            node_configs['ip'] = file_configs[config]
        else:
            node_configs[config.lower()] = file_configs[config]

    return node_configs


def __validate_configs(node_configs:dict):
    """
    format and validate configurations
    :args:
        node_configs
    :param:
        status:bool
    :return:
        node_configs
    """
    status = True
    for config in node_configs:
        if node_configs[config].lower() == 'true':
            node_configs[config] = True
        elif node_configs[config].lower() == 'false':
            node_configs[config] = False
        else:
            try:
                node_configs[config] = int(node_configs[config])
            except:
                pass

    for key in ['node_type', 'node_name', 'company_name', 'ledger_conn', 'license_key']:
        if key not in node_configs:
            print(f"Failed to locate '{key}'")
            status = False

    if status is False:
        print("Failed to locate one or more critical params, cannot continue...")
        exit(1)

    return node_configs


def declare_directories(anylog_conn:AnyLogConnector=None, anylog_path:str=ROOT_DIR, exception:bool=False):
    """
    create AnyLog directories
    :args:
        anylog_path:str - AnyLog root path
        exceptions;bool - whether to print exceptions
    :params:
        status:bool - status
    """
    anylog_path = os.path.expandvars(os.path.expandvars(anylog_path))
    status = set_anylog_home(anylog_conn=anylog_conn, root_path=anylog_path, remote_destination=None, view_help=False, exception=exception)
    if status is False:
        print(f"Failed to set {anylog_path} as home")
    else:
        if create_directories(anylog_conn=anylog_conn, remote_destination=None, view_help=False, exception=exception) is False:
            print(f"Failed to create directories in {anylog_path}. Cannot continue...")
            status = False

    if status is False:
        exit(1)


def get_configs(anylog_conn:AnyLogConnector, config_file:str, exception:bool=False):
    """
    Get and merge configurations
    :process:
        1. get configs from file + anylog node
        2. merge configurations
        3. format configurations + validate key needed params exist
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        config_file:str - configuration file
        exception:bool - whether to print exceptions
    :params:
        file_configs:dict - configuration from file
        anylog_configs:dict - configurations from AnyLog node
        node_configs:dict - merged configurations to be used in deployment
    :return:
        node_configs
    """
    file_configs = read_configs(config_file=config_file, exception=exception)
    anylog_configs = get_dictionary(anylog_conn=anylog_conn, json_format=True, remote_destination=None, view_help=False, exception=exception)
    node_configs = __merge_configs(file_configs=file_configs, anylog_configs=anylog_configs)
    return __validate_configs(node_configs=node_configs)

