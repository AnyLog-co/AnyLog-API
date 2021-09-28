import argparse
import os

import __init__
import anylog_api
import blockchain_cmd
import get_cmd
import post_cmd
import config

import master
import operator_node
import file_deployment
import publisher
import query


def __set_config(conn:anylog_api.AnyLogConnect, config_file:str, post_config:bool=False, exception:bool=False)->dict:
    """
    Set configuration object containing data from both file & pre-set within AnyLog
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        config_file:str - User config file
        post_config:bool - whether to update config within AnyLog
        excpetion:bool - whether to print exception or not
    :params:
        config_data:dict - config values
        import_config:dict - pre-set config from AnyLog
    :return:
        config_data
    """
    # Update configuration file on AnyLog:
    # --> read config file
    # --> add hostname
    # --> PULL config from AnyLog
    # --> POST full config to AnyLog
    config_data = {}
    config_file = os.path.expandvars(os.path.expanduser(config_file))

    # Attempt to read config file
    if os.path.isfile(config_file):
        config_data = config.read_config(config_file)

    # Update config object with pre-set commands
    if config_data != {}:
        hostname = get_cmd.get_hostname(conn=conn, exception=exception)
        if hostname is not None:
            config_data['hostname'] = hostname

        import_config = config.import_config(conn=conn, exception=exception)
        if import_config != {}:
            config_data = {**import_config, **config_data}

        if post_config is True:
            config.post_config(conn=conn, config=config_data, exception=exception)


    return config_data



def __default_components(conn:anylog_api.AnyLogConnect, node_type:str, master_node:str, deployment_file:str=None, exception:bool=False):
    """
    Deploy components that are required by all nodes
        - blockchain sync
        - scheduler 1 
        - extra commands from file
        - threshold for Publisher & Operator
    :args:
        conn:anylog_api.AnyLogConnect - Connection to AnyLog
        node_type:str - Node type
        master_node:str - Master IP & Port
        deployment_file:str - file to execute
        exception:bool - Exception print
    """
    # blockchain sync
    if not blockchain_cmd.blockchain_sync(conn=conn, source='master', time='1 minute', connection=master_node, exception=exception):
        print('Failed to set blockchain sync process')

    # Post scheduler 1
    if not post_cmd.start_scheduler1(conn=conn, exception=exception):
        print('Failed to start scheduler 1')

    # execute deployment file
    if deployment_file is not None:
        full_path = os.path.expandvars(os.path.expanduser(deployment_file))
        if os.path.isfile(full_path) and deployment_file is not None:
            file_deployment.deploy_file(conn=conn, deployment_file=full_path)
        elif deployment_file is not None:
            print("File: '%s' does not exist" %     full_path)

def deployment():
    """
    Based on configuration file, deploy a specific node
    :requirement: 
        an empty node for each node being deployed 
    :process: 
        1. Create connection to AnyLog
        2. Check REST connection works
        3. Set config - 4 part process  
        4. Based on node_type (from config) deploy a node via REST   
    :positional arguments:
        rest_conn             REST connection information
        config_file           AnyLog INI config file
    :optional arguments:
        -h, --help                              show this help message and exit
        -a, --auth              AUTH            REST authentication information (default: None)
        -t, --timeout           TIMEOUT         REST timeout period (default: 30)
        -f, --script-file       SCRIPT_sFILE     If set run commands in file at the end of the deployment (default: None)
        -u, --update-config     UPDATE_CONFIG   whether to update config within AnyLog                   (default: False)
        -l, --location          LOCATION        If set to True & location not in config, add lat/long coordinates for new policies (default: True)
        -e, --exception         EXCEPTION       print exception errors (default: False)
    :params: 
       anylog_conn:anylog_api.AnyLogConnect - Connection to AnyLog 
       config_file:str - full path from args.config_file
       config_data:dict - config data (from file + hostname + AnyLog) 
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn',       type=str,   default='127.0.0.1:2049', help='REST connection information')
    parser.add_argument('config_file',     type=str,   default=None, help='AnyLog INI config file')
    parser.add_argument('-a', '--auth',    type=tuple, default=None, help='REST authentication information')
    parser.add_argument('-t', '--timeout', type=int,   default=30,   help='REST timeout period')
    parser.add_argument('-f', '--script-file',   type=str,   default=None, help='If set run commands in file at the end of the deployment (must include path)')
    parser.add_argument('-u', '--update-config', type=bool, nargs='?', const=True,  default=False, help='Whether to update config within AnyLog')
    parser.add_argument('-l', '--location',      type=bool, nargs='?', const=False, default=True,  help='If set to True & location not in config, add lat/long coordinates for new policies')
    parser.add_argument('-e', '--exception',     type=bool, nargs='?', const=True,  default=False, help='print exception errors')
    args = parser.parse_args()

    # Connect to AnyLog REST 
    anylog_conn = anylog_api.AnyLogConnect(conn=args.rest_conn, auth=args.auth, timeout=args.timeout)

    # Validate REST node is accessible 
    if get_cmd.get_status(conn=anylog_conn, exception=args.exception) is False: 
        print('Failed to get status from %s, cannot continue' % args.rest_conn)
        exit(1) 

    # Get config
    config_data = __set_config(conn=anylog_conn,config_file=args.config_file, post_config=args.update_config, exception=args.exception)
    if config_data == {}:
        print("Failed to extract config from: '%s'" % args.config_file)
        exit(1)

    if config.validate_config(config=config_data) is True:
        if config_data['node_type'] == 'master':
            master.master_init(conn=anylog_conn, config=config_data, location=args.location, exception=args.exception)
        elif config_data['node_type'] == 'query':
            query.query_init(conn=anylog_conn, config=config_data, location=args.location, exception=args.exception)
        elif config_data['node_type'] == 'publisher':
            publisher.publisher_init(conn=anylog_conn, config=config_data, location=args.location, exception=args.exception)
        elif config_data['node_type'] == 'operator':
            operator_node.operator_init(conn=anylog_conn, config=config_data, location=args.location, exception=args.exception)

        __default_components(conn=anylog_conn, node_type=config_data['node_type'], master_node=config_data['master_node'],
                             deployment_file=args.script_file, exception=args.exception)
    

        print('List of running processes for node type: %s' % config_data['node_type'])
        print(get_cmd.get_processes(conn=anylog_conn, exception=args.exception))


if __name__ == '__main__':
    deployment() 
