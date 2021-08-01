import argparse
import os 

def deployment(): 
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('config_file', type=str, default=None, help='AnyLog INI config file')
    args = parser.parse_args()

