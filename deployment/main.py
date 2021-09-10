import argparse
import os

import __init__
import anylog_api
import get_cmd
import config

import master
import operator_node
import publisher
import query


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
        -h, --help                      show this help message and exit
        -a, --auth          AUTH        REST authentication information (default: None)
        -t, --timeout       TIMEOUT     REST timeout period (default: 30)
        -l, --location      LOCATION    If set to True & location not in config, add lat/long coordinates for new policies
        -e, --exception     EXCEPTION   print exception errors (default: False)
    :params: 
       anylog_conn:anylog_api.AnyLogConnect - Connection to AnyLog 
       config_file:str - full path from args.config_file
       config_data:dict - config data (from file + hostname + AnyLog) 
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn',         type=str,   default='127.0.0.1:2049', help='REST connection information') 
    parser.add_argument('config_file',       type=str,   default=None,             help='AnyLog INI config file')
    parser.add_argument('-a', '--auth',      type=tuple, default=None,             help='REST authentication information') 
    parser.add_argument('-t', '--timeout',   type=int,   default=30,               help='REST timeout period') 
    parser.add_argument('-l', '--location',  type=bool,  nargs='?', const=True,    default=False, help='If set to True & location not in config, add lat/long coordinates for new policies') 
    parser.add_argument('-e', '--exception', type=bool,  nargs='?', const=True,    default=False, help='print exception errors')
    args = parser.parse_args()
    
    
    # Connect to AnyLog REST 
    anylog_conn = anylog_api.AnyLogConnect(conn=args.rest_conn, auth=args.auth, timeout=args.timeout)

    # Validate REST node is accessible 
    if get_cmd.get_status(conn=anylog_conn, exception=args.exception) is False: 
        print('Failed to get status from %s, cannot continue' % args.rest_conn)
        exit(1) 

    # Update configuration file on AnyLog: 
    # --> read config file 
    # --> add hostname
    # --> PULL config from AnyLog
    # --> POST full config to AnyLog 
    config_file = os.path.expandvars(os.path.expanduser(args.config_file))
    if os.path.isfile(config_file): 
        config_data = config.read_config(config_file) 
    if not os.path.isfile(config_file) or config == {}: 
        print('Failed to extract config from %s' % config_file) 
        exit(1) 

    hostname = get_cmd.get_hostname(conn=anylog_conn, exception=args.exception) 
    if hostname is not None:
        config_data['hostname'] = hostname
    
    import_config = config.import_config(conn=anylog_conn, exception=args.exception)
    for key in import_config:
        if key not in config_data: 
            config_data[key] = import_config[key] 

    config.post_config(conn=anylog_conn, config=config_data, exception=args.exception)

    if 'node_type' in config_data and config.validate_config(config=config_data) is True:
        status = True
        if config_data['node_type'] == 'master':
            master.master_init(conn=anylog_conn, config=config_data, location=args.location, exception=args.exception)
        elif config_data['node_type'] == 'query':
            query.query_init(conn=anylog_conn, config=config_data, location=args.location, exception=args.exception)
        elif config_data['node_type'] == 'publisher':
            publisher.publisher_init(conn=anylog_conn, config=config_data, location=args.location, exception=args.exception)
        elif config_data['node_type'] == 'operator':
            operator_node.operator_init(conn=anylog_conn, config=config_data, location=args.location, exception=args.exception)
        else:
            print('Unsupported node type: %s' % config['node_type'])
            status = False
        if status is True:
            print('Lis of running processes for node type: %s' % config_data['node_type'])
            print(get_cmd.get_processes(conn=anylog_conn, exception=args.exception))


if __name__ == '__main__':
    deployment() 
