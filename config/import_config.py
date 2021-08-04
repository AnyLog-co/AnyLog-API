import ast 
import configparser
import os 
import sys

rest_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/rest')) 

sys.path.insert(0, rest_dir) 

import rest 
import get_cmd
 
def import_config(conn:rest.AnyLogConnect, exception:bool=False)->dict: 
    """
    Extract parameters from AnyLog dictionary into dictionary  
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :param: 
        data:dict - formatted results from dictionary
        dictionary:str - raw results from get_cmd.get_dictionary 
    :return: 
        data 
    """
    data = {} 
    dictionary = get_cmd.get_dictionary(conn=conn, exception=exception)
    if dictionary != None: 
        for value in dictionary.split('\n'):
            if value != '\r' and value != '':  
                data[value.split(':')[0].rstrip().lstrip()] = value.split(':')[-1].split('\r')[0].rstrip().lstrip()

    return data 

