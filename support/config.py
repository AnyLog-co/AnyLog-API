import configparser
import os
import sys 

rest_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/rest')) 
sys.path.insert(0, rest_dir) 

import get_cmd
import post_cmd
import anylog_api


def read_config(config_file:str)->dict: 
    """
    Read INI configuration & store in dict 
    :args: 
        config_file:str - configuraiton file
    :params: 
        data:dict - data from config file that files to to be added to AnyLog Network
        config_full_path:str - full path of configuration file 
    :return: 
        data 
    """
    data = {} 
    config = configparser.ConfigParser()
    if os.path.isfile(config_file):
        try:
            config.read(config_file)
        except Exception as e: 
            if exception == True: 
                print('Failed to read config file: %s (Error: %s)' % (config_file, e))
    else:
        print('File %s not found' % config_file) 
    
    try: 
        for section in config.sections():
            for key in config[section]:
                data[key] = config[section][key] 
    except Exception as e:
        print('Failed to extract variables from config file (Error: %s)' % e)

    return data 

   

def post_config(conn:anylog_api.AnyLogConnect, config:dict, exception:bool=False)->bool: 
    """
    POST config to AnyLog
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        config:dict - configuration to POST 
        exception:bool - whether or not to print error to screen 
    :param: 
       status:bool 
    :return: 
        status
    """
    statuses = [] 
    for key in config: 
        status = post_cmd.post_value(conn=conn, key=key, value=config[key], exception=exception)
        if status == False and exception == True: 
            print('Failed to add object to dictionary on %s (key: %s | value: %s)' % (conn.conn, key, config[key]))
        statuses.append(status)

    status = True
    if False in statuses: 
        status = False

    return status 
 
def import_config(conn:anylog_api.AnyLogConnect, exception:bool=False)->dict: 
    """
    Extract parameters from AnyLog dictionary into dictionary  
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog RESt 
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
                data[value.split(':', )[0].rstrip().lstrip()] = value.split(':', 1)[-1].split('\r')[0].rstrip().lstrip()

    return data 

