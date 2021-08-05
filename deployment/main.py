import argparse
import os 
import sys 

config_dir = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/config'))
rest_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/rest')) 
support_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/support')) 

sys.path.insert(0, config_dir)
sys.path.insert(0, rest_dir) 
sys.path.insert(0, support_dir) 

import get_cmd

from import_config import import_config
from post_config   import post_config 
from read_config   import read_config
from rest          import AnyLogConnect
 
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
        -e, --exception     EXCEPTION   print exception errors (default: False)
    :params: 
       anylog_conn:rest.AnyLogConnect - Connection to AnyLog 
       config_file:str - full path from args.config_file
       config:dict - config data (from file + hostname + AnyLog) 
    """
    config = {} 
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn',         type=str,   default='127.0.0.1:2049', help='REST connection information') 
    parser.add_argument('config_file',       type=str,   default=None,             help='AnyLog INI config file')
    parser.add_argument('-a', '--auth',      type=tuple, default=None,             help='REST authentication information') 
    parser.add_argument('-t', '--timeout',   type=int,   default=30,               help='REST timeout period') 
    parser.add_argument('-e', '--exception', type=bool,  nargs='?', const=True,    default=False, help='print exception errors')
    args = parser.parse_args()
    
    
    # Connect to AnyLog REST 
    anylog_conn = AnyLogConnect(conn=args.rest_conn, auth=args.auth, timeout=args.timeout)

    # Validate REST node is accessible 
    if get_cmd.get_status(conn=anylog_conn, exception=args.exception) == False: 
        print('Failed to get status from %s, cannot continue' % args.rest_conn)
        exit(1) 

    # Update configuration file on AnyLog: 
    # --> read config file 
    # --> add hostname
    # --> PULL config from AnyLog
    # --> POST full config to AnyLog 
    config_file = os.path.expandvars(os.path.expanduser(args.config_file))
    if os.path.isfile(config_file): 
        config = read_config(config_file) 
    if not os.path.isfile(config_file) or config == {}: 
        print('Failed to extract config from %s' % config_file) 
        exit(1) 
    
    hostname = get_cmd.get_hostname(conn=anylog_conn, exception=args.exception) 
    if hostname != None: 
        config['hostname'] = hostname

    config.update(import_config(conn=anylog_conn, exception=args.exception))

    if post_config(conn=anylog_conn, config=config, exception=args.exception) == False: 
        print('Failed to POST config into AnyLog Node on %s' % args.rest_conn)
    print(config)  
    if 'node_type' in config: 
        if config['node_type'] == 'master': 
            pass 
        elif config['node_type'] == 'query': 
            pass 
        elif config['node_typ'] == 'publisher':
            pass 
        elif config['node_type'] == 'operator': 
            pass 
        else: 
            print('Unsupported node type: %s' % config['node_type'])
    else: 
        print('Missing node_type in config')


if __name__ == '__main__': 
    deployment() 
