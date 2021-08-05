import os
import sys 

import get_cmd 
import rest 

support_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/support')) 
sys.path.insert(0, support_dir) 

import errors


def post_value(conn:rest.AnyLogConnect, key:str, value:str, exception:bool=False)->bool: 
    """
    POST value to dictionary
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog
        key:str - dictionary key
        value:str - value for corresponding key
        exception:bool - whether or not to print error to screen 
    :param: 
        status:bool
        cmd:str - command to execute
    :return: 
        status
    """
    status = True 
    cmd = "set %s=%s" % (key, value)
    r, error = conn.post(command=cmd)
     
    if errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception) == True:  
        status = False 

    return status 
 
def post_scheduler1(conn:rest.AnyLogConnect, exception:bool=False)->bool: 
    """
    POST scheduler 1 to AnyLog 
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog
        exception:bool - whether or not to print error to screen 
    :params: 
        status:bool 
        cmd:str: 
    """
    status = True
    cmd = "run scheduler 1" 

    if 'not declared' in get_cmd.get_scheduler(conn=conn, scheduler_name='1', exception=exception): 
        r, error = conn.post(command=cmd)
        if errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception) == True:  
            status = False 

    return status 
