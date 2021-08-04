import os 
import sys 

rest_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/rest')) 
sys.path.insert(0, rest_dir) 
import rest 

def post_value(conn:rest.AnyLogConnect, key:str, value:str, exception:bool=False)->bool: 
    """
    POST value to dictionary
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog
        key:str - dictionary key
        value:str - value for corresponding key
        exception:bool - whether or not to print error to screen 
    :param: 
       cmd:str - command to execute
    :return: 
        status
    """
    status = True 
    cmd = "set %s=%s" % (key, value)
    
    r, error = conn.post(command=cmd)

    if r == False and isinstance(error, str): 
        if exception == True: 
            print('Failed to excute POST on %s (Error: %s)' % (conn.conn, error)) 
        status = False 
    elif r == False and isinstance(error, int):
        if exception == True: 
            print('Failed to execute POST on %s due to network error %s' % (conn.conn, error))
        status = False 
 
    return status 
    

def post_config(conn:rest.AnyLogConnect, config:dict, exception:bool=False)->bool: 
    """
    POST config to AnyLog
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog
        config:dict - configuration to POST 
        exception:bool - whether or not to print error to screen 
    :param: 
       status:bool 
    :return: 
        status
    """
    statuses = [] 
    for key in config: 
        status = post_value(conn=conn, key=key, value=config[key], exception=exception)
        if status == False and exception == True: 
            print('Failed to add object to dictionary on %s (key: %s | value: %s)' % (conn.conn, key, config[key]))
        statuses.append(status)

    status = True
    if False in statuses: 
        status = False

    return status 
