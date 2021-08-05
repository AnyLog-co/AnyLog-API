import os
import sys 

support_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/support')) 
sys.path.insert(0, support_dir) 

import error


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
     
    if error.post_error(conn=conn, r=r, error=error, exception=exception) == True:  
        if exception == True: 
            print('Failed to add key: %s & value: %s pair to dictionary' % (key, value)) 
        status = False 

    return status 
 
