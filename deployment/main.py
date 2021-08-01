import argparse
import os 

def deployment(): 
    """
    Based on configuration file, deploy a specific node
    :positional arguments:
        config_file  AnyLog INI config file
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('config_file', type=str, default=None, help='AnyLog INI config file')
    args = parser.parse_args()
    
    config_file = os.path.expandvars(os.path.expanduser(config_file))

if __name__ == '__main__': 
    deployment()
