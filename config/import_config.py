import ast 
import configparser
import os 

def config_import(config_file:str)->dict: 
    """
    Read INI configuration file & store to dictionary 
    :args: 
        config_file:str - configuraiton file
    :params: 
        data:dict - data from config file that files to to be added to AnyLog Network
        config_full_path:str - full path of configuration file 
        config:configparser.ConfigParser - call to the configuration file 
    :return: 
        data 
    """
    data = {} 
    config = configparser.ConfigParser()
    if os.path.isfile(config_full_path):
        try:
            config.read(config_file)
        except Exception as e: 
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
                try: 
                    data[key] = os.path.expandvars(os.path.expanduser(value))
                except: 
                    data[key] = value 
    return data 

