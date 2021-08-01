import ast 
import configparser
import os
import rest

def config_import(config_file:str, conn:str, timeout:float=10, auth:tuple=None, exception:bool=True)->dict: 
    """
    Read INI configuration file & set in AnyLog as dictionary params. If fails to send, keeps in data object 
    :args: 
        config_file:str - configuraiton file
        conn:str - REST connection information 
        timeout:float - REST timeout 
        auth:tuple - REST authentication info
        exception:bool - whether to print exception(s) or not
    :params: 
        data:dict - data from config file that files to to be added to AnyLog Network
        config_full_path:str - full path of configuration file 
        config:configparser.ConfigParser - call to the configuration file 
    :return: 
        data 
    """
    data = {} 
    config_full_path = os.path.expandvars(os.path.expanduser(config_file))
    config = configparser.ConfigParser()
    if os.path.isfile(config_full_path):
        try:
            config.read(config_full_path)
        except Exception as e: 
            if exception == True: 
                print('Failed to read config file: %s (Error: %s)' % (config_file, e))
    else:
        if exception == True: 
            print('File %s not found' % config_file) 
    
    try: 
        for section in config.sections():
            for key in config[section]:
                try:
                    value = ast.literal_eval(config[section][key])
                except:
                    value = config[section][key] 
                status = post_config(conn=conn, timeout=timeout, auth=auth, exception=exception, key=key, value=value)
                if status == False and exception == True: 
                    data[key.lower()] = value
    except Exception as e:
        if exception == True: 
            print('Failed to extract variables from config file (Error: %s)' % e)
    return data 

def post_config(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True, key:str=None, value:str=None)->bool: 
    """
    POST param to AnyLog 
    :args: 
        conn:str - REST connection information 
        timeout:float - REST timeout 
        auth:tuple - REST authentication info
        exception:bool - whether to print exception(s) or not
        key:str - AnyLog variable 
        value:str - value for key
    :params: 
        conn:cmd - command to execute 
    :return: 
        data 
    """
    cmd="set %s=%s" % (key, value) 
    status = rest.post(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    if status == False and exception == True: 
        print('Failed to execute POST key value pair to AnyLog dictionary [key: %s | value: %s]' % (key, value))
    return status 

def config_export(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True, data:dict={})->dict: 
    """
    Extract parameters from AnyLog dictionary 
    :args: 
        data:dict - original data set that failed to send into AnyLog dictionary 
        config_data:dict - read config data 
        conn:str - REST connection information 
        timeout:float - REST timeout 
        auth:tuple - REST authentication info
        exception:bool - whether to print exception(s) or not
    :param: 
        output:str - raw results from GET 
        data:dict - data from dictionary
    :return: 
    """
    output = rest.get(conn=conn, cmd="get dictionary", timeout=timeout, auth=auth, exception=exception) 
    if not output and exception == True: 
        print('Failed to get parameters from AnyLog dictionary') 

    if output != None:  
        for param in output.split('\n'):
            key = param.split(':', 1)[0].replace('\r', '').rstrip().lstrip().lower() 
            try: 
                value = ast.literal_eval(param.split(':', 1)[-1].replace('\r', '').rstrip().lstrip())
            except: 
                value = param.split(':', 1)[-1].replace('\r', '').rstrip().lstrip() 
            if key != "" and value != "" :
                data[key] = value

    return data 

