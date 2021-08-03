import ast 
import configparser
import os 
import sys

rest_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/rest')) 

sys.path.insert(0, rest_dir) 

import get_cmd
from read_config import read_config
 
def import_config(conn:str, auth:tuple=None, timeout:int=30): 
    """
    Extract parameters from AnyLog dictionary 
    :args: 
        conn:str - REST connection information 
        timeout:float - REST timeout 
        auth:tuple - REST authentication info
    :param: 
        output:str - raw results from GET 
        data:dict - data from dictionary
    :return: 
    """
    

