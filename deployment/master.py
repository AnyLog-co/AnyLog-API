import os 
import sys 

REST_DIR = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/rest'))

sys.path.insert(0, REST_DIR) 
from get import rest_query

def master_init(config_data:dict): 
    
