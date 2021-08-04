import argparse
import os 
import sys 

#import master 

config_dir = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/config'))
rest_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/rest')) 
support_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/support')) 

sys.path.insert(0, config_dir)
sys.path.insert(0, rest_dir) 
sys.path.insert(0, support_dir) 

import get_cmd

from read_config  import read_config
from rest import AnyLogConnect
 
def deployment(): 
    """
    Based on configuration file, deploy a specific node
    :requirement: 
        an empty node for each node being deployed 
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
    """
    config = {} 
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn',         type=str,   default='127.0.0.1:2049', help='REST connection information') 
    parser.add_argument('config_file',       type=str,   default=None,             help='AnyLog INI config file')
    parser.add_argument('-a', '--auth',      type=tuple, default=None,             help='REST authentication information') 
    parser.add_argument('-t', '--timeout',   type=int,   default=30,               help='REST timeout period') 
    parser.add_argument('-e', '--exception', type=bool,  nargs='?', const=True,    default=False, help='print exception errors')
    args = parser.parse_args()
    
    anylog_conn = AnyLogConnect(conn=args.rest_conn, auth=args.auth, timeout=args.timeout)
    print(get_cmd.get_status(conn=anylog_conn))

    """
    # Extract information from configuration file 
    config_file = os.path.expandvars(os.path.expanduser(args.config_file))
    if os.path.isfile(config_file): 
        config = read_config(config_file) 
    if not os.path.isfile(config_file) or config == {}: 
        print('Failed to extract config from %s' % config_file) 
        exit(1) 

    if not get_cmd.get_status(args.rest_conn): 
        print('Failed to connect to AnyLog instance using %s' % args.rest_conn)
        exit(1) 
    
    # Add pre-existing config from AnyLog
    config.update(get_cmd.get_dictionary(args.rest_conn))
 
    hostname = get_cmd.get_hostname(args.rest_conn)
    if hostname != None: 
        config['hostname'] = hostname

    if 'location' not in config: 
        config['location'] = get_location() 
    print(config) 
    exit(1) 
    # Deploy node based on node_type 
    if config['node_type'] == 'master': 
        #master.master_init(config) 
        pass
    elif config['node_type'] == 'operator': 
        pass 
    elif config['node_type'] == 'query': 
        pass 
    elif config['node_type'] == 'publisher': 
        pass 
    else: 
        print('Invalid node type: %s' % config['node_type']) 
        exit(1) 
    """
if __name__ == '__main__': 
    deployment()
