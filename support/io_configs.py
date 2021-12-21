import configparser
import os 
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).rsplit('support', 1)[0]
rest_dir = os.path.join(ROOT_PATH, 'rest')
support_dir = os.path.join(ROOT_PATH, 'support')
sys.path.insert(0, rest_dir)
sys.path.insert(0, support_dir)

import anylog_api
import get_cmd
import post_cmd


def read_config(config_file:str)->(dict, list):
    """
    Read INI configuration & store in dict 
    :args: 
        config_file:str - configuraiton file
    :params: 
        data:dict - data from config file that files to to be added to AnyLog Network
        error_msgs:list - if something fails, list of error messages
        config_full_path:str - full path of configuration file 
    :return: 
        data 
    """
    data = {}
    error_msgs = []
    config = configparser.ConfigParser()
    if os.path.isfile(config_file):
        try:
            config.read(config_file)
        except Exception as e: 
            error_msgs.append('Failed to read config file: %s (Error: %s)' % (config_file, e))
    else:
        error_msgs.append('File %s not found' % config_file)

    if error_msgs == []:
        try:
            for section in config.sections():
                if section not in data:
                    data[section] = {}
                for key in config[section]:
                    data[section][key] = config[section][key].replace('"', '')
        except Exception as e:
            error_msgs.append('Failed to extract variables from config file (Error: %s)' % e)

    return data, error_msgs


def post_config(conn:anylog_api.AnyLogConnect, config:dict, exception:bool=False)->bool:
    """
    POST config to AnyLog
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        config:dict - configuration to POST 
        exception:bool - whether or not to print error to screen
    :params:
        status
    """
    status = True
    for key in config: 
        if not post_cmd.post_value(conn=conn, key=key, value=config[key], exception=exception):
            status = False
            if exception is True:
                print('Failed to add object to dictionary on %s (key: %s | value: %s)' % (conn.conn, key, config[key]))
    return status


def import_config(conn:anylog_api.AnyLogConnect, env_params:dict, exception:bool=False)->dict:
    """
    Extract parameters from AnyLog dictionary into dictionary  
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog RESt
        env_params:dict - configurations params
        exception:bool - whether to print errors to screen 
    :param:
        dictionary:str - raw results from get_cmd.get_dictionary 
    :return: 
        updated env_params with content from AnyLog dictionary
    """
    dictionary = get_cmd.get_dictionary(conn=conn, exception=exception)
    if dictionary is not None:
        for key in dictionary:
            if key.upper() not in env_params:
                env_params[key.upper()] = dictionary[key]
    return data 


def format_configs(env_configs:dict)->dict:
    """
    format configurations to be used for docker call
    :example:
        {"general": {"node_name": "new-node", "company": "AnyLog Co."}} --> {"NODE_NAME": "new-node", "COMPANY": "AnyLog co."}
    :args:
        env_configs:dict - environment configurations
    :params:
        env_params:dict - formatted env_configs
    :return:
        env_params
    """
    env_params = {}
    for key in env_configs:
        for param in env_configs[key]:
            env_params[param.upper()] = env_configs[key][param]

    return env_params