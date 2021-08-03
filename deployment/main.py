import argparse
import os 
import sys 

import master 

config_dir = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/config'))
rest_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/rest')) 

sys.path.insert(0, config_dir)
sys.path.insert(0, rest_dir) 

import get_cmd

from get_location import get_location 
from read_config  import read_config
 
def deployment(): 
    """
    Based on configuration file, deploy a specific node
    :requirement: 
        an empty node for each node being deployed 
    :positional arguments:
        rest_conn    REST connection information 
        config_file  AnyLog INI config file
    """
    config = {} 
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn',   type=str, default='127.0.0.1:2049', help='REST connection information') 
    parser.add_argument('config_file', type=str, default=None,             help='AnyLog INI config file')
    args = parser.parse_args()
    
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
        master.master_init(config) 
    elif config['node_type'] == 'operator': 
        pass 
    elif config['node_type'] == 'query': 
        pass 
    elif config['node_type'] == 'publisher': 
        pass 
    else: 
        print('Invalid node type: %s' % config['node_type']) 
        exit(1) 

if __name__ == '__main__': 
    deployment()
