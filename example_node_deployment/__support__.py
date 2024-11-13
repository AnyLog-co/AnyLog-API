from logging import error

import anylog_api.anylog_connector as anylog_connector
import anylog_api.generic.get as generic_get
import anylog_api.generic.post as generic_post
import __support_files__ as support_files

def validate_configs(params:dict):
    # database params
    if 'db_type' not in params:
        print('Missing database type, cannot continue...')
        exit(1)
    elif params['db_type'] != 'sqlite':
        error = ""
        for param in ['db_user', 'db_passwd', 'db_ip', 'db_port']:
            if param not in params:
                if error == "":
                    error = f"Missing {param}"
                else:
                    error += f", {param}"
        if error != "":
            print(error + ", cannot continue...")
            exit(1)

    # ledger conn
    if 'ledger_conn' not in params:
        print(f'Missing ledger conn value, cannot continue...')
        exit(1)

    # general information for node
    error = ""
    for param in ['node_type', 'node_name', 'anylog_server_port', 'anylog_rest_port']:
        if param not in params:
            if param not in params:
                if error == "":
                    error = f"Missing {param}"
                else:
                    error += f", {param}"
    if error != "":
        print(error + ", cannot continue...")
        exit(1)

    # ip connection information
    if all(param not in params for param in ['ip', 'external_ip', 'overlay_ip']):
        print(f"Missing networking IP connection information, cannot continue...")
        exit (1)


def extract_ips(params:dict):
    """
    Extract IP values based on configurations
    :args:
        params:dict - configurations
    :params:
        local_ip:str - local ip address
        ip:str - ip
    :return:
        ip, local_ip
    """
    # set ips
    local_ip = None
    if 'tcp_bind' in params and params['tcp_bind'] is True:
        if 'overlay_ip' in params:
            ip = params['overlay_ip']
        elif 'ip' in params:
            ip = params['ip']
        elif 'external_ip' in params:
            ip = params['external_ip']
    else:
        if all(param in params for param in ['external_ip', 'overlay_ip']):
            ip = params['external_ip']
            local_ip = params['overlay_ip']
        elif all(param in params for param in ['external_ip', 'ip']):
            ip = params['external_ip']
            local_ip = params['ip']
        elif all(param in params for param in ['ip', 'overlay_ip']):
            ip = params['ip']
            local_ip = params['overlay_ip']

    return ip, local_ip


def validate_connection(conn:anylog_connector.AnyLogConnector, exception:bool=False):
    """
    Validate whether the node is running - if fails code
    """
    # validate node is running
    if generic_get.get_status(conn=conn, destination=None, view_help=False, return_cmd=False,
                              exception=exception) is False:
        print(f"Failed to communicated with {conn.conn}. cannot continue...")
        exit(1)


def set_dictionary(conn:anylog_connector.AnyLogConnector, config_files:str, exception:bool=False):
    """
    Set node configurations
    :process:
        1. get default configs
        2. read config file
        3. merge comfigs
        4. if node_type is missing goto node_state
    """
    # get preset / default params
    generic_params = generic_get.get_dictionary(conn=conn, json_format=True, destination="", view_help=False,
                                                return_cmd=False, exception=exception)
    file_configs = {}

    # get configs from file
    if config_files is not None:
        file_configs = support_files.read_configs(config_file=config_files, exception=exception)
    # merge configs
    if file_configs:
        for config in file_configs:
            if file_configs[config]:
                generic_params[config.lower()] = file_configs[config]

    err_msg = ""
    for config in ['node_type', 'node_name', 'company_name', 'ledger_conn', 'db_type']:
        if config not in generic_params or generic_params[config] == "":
            if err_msg == "":
                err_msg = f"Missing key config param(s). Param List: {config}"
            else:
                err_msg += f", {config}"
    if err_msg != "":
        raise err_msg
    generic_post.set_params(conn=conn, params=generic_params, destination=None, view_help=False,
                            exception=exception)
    return generic_params


def configure_directories(conn:anylog_connector.AnyLogConnector, anylog_path:str, exception:bool=False):
    """
    Configure directories in node
    :process:
        1. st anylog home path
        2. create work directories
    """
    generic_post.set_path(conn=conn, path=anylog_path, destination=None, view_help=False, returnn_cmd=False,
                          exception=exception)

    generic_post.create_work_dirs(conn=conn, destination=None, view_help=False, return_cmd=False, exception=exception)
