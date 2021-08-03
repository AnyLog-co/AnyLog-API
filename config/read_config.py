import ast 
import configparser
import os

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
                try: 
                    value = ast.literal_eval(config[section][key]) 
                except: 
                    value = config[section][key]
                data[key] = value
    except Exception as e:
        print('Failed to extract variables from config file (Error: %s)' % e)
    return data 
