import argparse
import os

# deployment scripts
import disconnect_node
import file_deployment
import master
import operator_node
import publisher
import query
import single_node

import __init__
# REST directory
import anylog_api
import blockchain_cmd
import dbms_cmd
import get_cmd
import post_cmd

# support directory
import config

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


def __default_start_components(conn:anylog_api.AnyLogConnect, config_file:str, deployment_file:str=None,
                               post_config:bool=False, exception:bool=False)->dict:
    """
    # Part 1
    Deploy components that are required by all nodes at the start of the code
        - validate connections
        - read config_file
        - validate node type
        - connect to SQLite system_query if node_type isn't Query
    # Part 2
    Deploy components that are required by all nodes
        - blockchain sync
        - scheduler 1
        - extra commands from file
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        config_file:str - User config file
        deployment_file:str - file to execute
        post_config:bool - whether to update config within AnyLog
        excpetion:bool - whether to print exception or not
    :params:
        config_data:dict - configs from file
        node_types:list - extraction of config['node_type'] as a list
        dbms_list:dict - extracted db list
    :return:
        config_data
    """
    # Check status
    if get_cmd.get_status(conn=conn, exception=exception) is False:
        print('Failed to get status from %s, cannot continue' % conn.conn)
        exit(1)

    # Read config & set node_types if len(config_data['node_type]) > 1
    config_data = __set_config(conn=conn, config_file=config_file, post_config=post_config, exception=exception)

    node_types = config_data['node_type'].split(',')
    if len(node_types) == 1:
        config_data['node_type'] = node_types[0]
    else:
        config['node_type'] = 'single_node'
        for node in node_types:
            if node not in ['master', 'publisher', 'operator', 'query']:
                print(("Node type %s isn't supported - supported node types: 'master', 'operator', 'publisher','query' "
                     + "or 'single_node'. Cannot continue...") % config['node_type'])
                exit(1)

    # Validate node type
    if config_data['node_type'].lower() not in ['master', 'publisher', 'operator', 'query', 'single_node']:
        print(("Node type %s isn't supported - supported node types: 'master', 'operator', 'publisher','query' or"
               +"'single_node'. Cannot continue...") % config_data['node_type'])
        exit(1)

    # Post config
    if post_config is True:
        if not config.post_config(conn=conn, config=config_data, exception=exception):
            print('Failed to post configuration into AnyLog dictionary')

    # configure system_query to run against SQLite if node type doesn't contain query node
    if config_data['node_type'] != 'query' and 'query' not in node_types:
        dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
        if 'system_query' not in dbms_list:
            if not dbms_cmd.connect_dbms(conn=conn, config={}, db_name='system_query', exception=exception):
                print('Failed to deploy system_query against %s node' % config['node_type'])

    # blockchain sync
    if not blockchain_cmd.blockchain_sync_scheduler(conn=conn, source='master', time='1 minute', master_node=config_data['master_node'], exception=exception):
        print('Failed to set blockchain sync process')
    
    # Start scheduler(s)
    for schedule in [0, 1]:
        if get_cmd.get_scheduler(conn=conn, scheduler_name=schedule, exception=exception) == 'not declared':
            if not post_cmd.start_exitings_scheduler(conn=conn, scheduler_id=schedule, exception=exception):
                print('Failed to start scheduler %s' % schedule)

    # execute deployment file
    if deployment_file is not None:
        full_path = os.path.expandvars(os.path.expanduser(deployment_file))
        if os.path.isfile(full_path) and deployment_file is not None:
            file_deployment.deploy_file(conn=conn, deployment_file=full_path)
        elif deployment_file is not None:
            print("File: '%s' does not exist" % full_path)

    return node_types, config_data


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
        rest_conn       REST_CONN       REST connection information
        config_file     CONFIG_FILE     AnyLog INI config file
    :optional arguments:
        -h, --help              HELP                     show this help message and exit
        -a, --auth              AUTH:tuple               REST authentication information                                                     [default: None]
        -t, --timeout           TIMEOUT:int              REST timeout period                                                                 [default: 30]
        -f, --script-file       SCRIPT_FILE:str          If set run commands in file at the end of the deployment (must include path)        [default: None]
        -u, --update-config     UPDATE_CONFIG:bool       Whether to update config within AnyLog dictionary                                   [default: False]
        -l, --disable-location  DISABLE_LOCATION:bool    If set to True & location not in config, add lat/long coordinates for new policies  [default: True]
        -s, --stop-node         STOP_NODE:bool           disconnect node without dropping corresponding policy                               [default: False]
        -c, --clean-node        CLEAN_NODE:bool          disconnect node and drop database and policy from blockchain                        [default: False]
        -e, --exception         EXCEPTION:bool           print exception errors                                                              [default: False]
    :params:
       anylog_conn:anylog_api.AnyLogConnect - Connection to AnyLog
       config_data:dict - config data (from file + hostname + AnyLog)
       node_types:list - config['node_type] if value contains more than one node
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn',       type=str,   default='127.0.0.1:2049', help='REST connection information')
    parser.add_argument('config_file',     type=str,   default=None, help='AnyLog INI config file')
    parser.add_argument('-a', '--auth',    type=tuple, default=None, help='REST authentication information')
    parser.add_argument('-t', '--timeout', type=int,   default=30,   help='REST timeout period')
    parser.add_argument('-f', '--script-file',   type=str,   default=None, help='If set run commands in file at the end of the deployment (must include path)')
    parser.add_argument('-u', '--update-config', type=bool, nargs='?', const=True,  default=False, help='Whether to update config within AnyLog dictionary')
    parser.add_argument('-l', '--disable-location', type=bool, nargs='?', const=False, default=True,  help='If set to True & location not in config, add lat/long coordinates for new policies')
    parser.add_argument('-s', '--stop-node',  type=bool, nargs='?', const=True,  default=False,  help='disconnect node without dropping corresponding policy')
    parser.add_argument('-c', '--clean-node', type=bool, nargs='?', const=True, default=False,  help='disconnect node and drop database and policy from blockchain')
    parser.add_argument('-e', '--exception',  type=bool, nargs='?', const=True, default=False, help='print exception errors')
    args = parser.parse_args()

    # Connect to AnyLog REST 
    anylog_conn = anylog_api.AnyLogConnect(conn=args.rest_conn, auth=args.auth, timeout=args.timeout)

    # prerequisite deployment
    node_types, config_data = __default_start_components(conn=anylog_conn, config_file=args.config_file,
                                                         deployment_file=args.script_file,
                                                         post_config=args.update_config, exception=args.exception)

    if args.stop_node is False and args.clean_node is False:
        if config_data['node_type'] == 'master':
            master.master_init(conn=anylog_conn, config=config_data, location=args.disable_location, exception=args.exception)
        if config_data['node_type'] == 'operator':
            operator_node.operator_init(conn=anylog_conn, config=config_data, location=args.disable_location, exception=args.exception)
        if config_data['node_type'] == 'publisher':
            publisher.publisher_init(conn=anylog_conn, config=config_data, location=args.disable_location, exception=args.exception)
        if config_data['node_type'] == 'query':
            query.query_init(conn=anylog_conn, config=config_data, location=args.disable_location, exception=args.exception)
        if config_data['node_type'] == 'single_node':
            single_node.single_node_init(conn=anylog_conn, config=config_data, node_types=node_types, location=args.disable_location,
                                         exception=args.exception)
    else:
        disconnect_node.disconnect_node(conn=anylog_conn, config=config_data, clean_node=args.clean_node, exception=args.exception)

    process_list = get_cmd.get_processes(conn=anylog_conn, exception=args.exception)
    if process_list is not None:
        print(process_list)
    else:
        print('Unable to get process list as such it is unclear whether an %s node was deployed...' % config['node_type'])


if __name__ == '__main__':
    deployment() 
