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

def post_publisher(conn:rest.AnyLogConnect, master_node:str, dbms_name:str, table_name:str, compress_json:bool=True, move_json:bool=True, exception:bool=False)->bool: 
    """
    Start publisher process
    :args: 
        conn:rest.AnyLogConnect connection to AnyLog
        master_node:str - Master node 
        dbms_name:str - database name 
        table_name:str - table name
        compress_json:bool - compress published file 
        move_json:bool - send file to bkup
        exception:bool - whether or not to print error to screen 
    :params: 
        status:bool 
        cmd:str - command to execute
    :return: 
        status
    """ 
    status = True
    if isinstance(compress_json, bool): 
        compress_json = str(compress_json).lower()
    else: 
        compress_json == 'true'
    if isinstance(move_json, bool): 
        move_json = str(move_json).lower()
    else: 
        move_json = 'true' 

    if 'Not declared' in get_cmd.get_processes(conn=conn, exception=exception).split('Publisher')[-1].split('\r')[0]:
        cmd = 'run publisher where compress_json=%s and move_json=%s and master_node=%s and dbms_name=%s and table_name=%s' % (compress_json, move_json, master_node, dbms_name, table_name)
        r, error = conn.post(command=cmd)
        if errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception) == True:  
            status = False 

    return status 

def set_immidiate_threshold(conn:rest.AnyLogConnect, exception:bool=False)->bool: 
    """
    Set threshold tto immidiate
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog
        exception:bool - whether or not to print error to screen 
    :params: 
        status:bool 
        cmd:str - command to execute 
    :return: 
        status 
    """
    status = True
    cmd = "set buffer threshold where write_immediate = true"

    r, error = conn.post(command=cmd)
    if errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception) == True: 
        status = False 

    return status 



