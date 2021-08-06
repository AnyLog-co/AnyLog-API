import os 
import sys 

import rest 

support_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/support')) 
sys.path.insert(0, support_dir) 

import errors


def get_help(conn:rest.AnyLogConnect, command:str=None): 
    """
    Execute 'help' against AnyLog. If command is set get help regarding command
    :args: 
        conn:rest.AnyLogConnect - Connection to AnyLog 
        command:str - command to get help on 
    :note: 
        function prints results rather than return it
    """
    help_stmt = 'help'     
    if command != None: 
        help_stmt += " " + command

    r, error = conn.get(command=help_stmt)
    if errors.get_error(conn=conn.conn, command=help_stmt, r=r, error=error, exception=True) == False: 
        try: 
            print(r.text)
        except Exception as e: 
            print('Failed to extract help information (Error: %s) ' % e)

def get_status(conn:rest.AnyLogConnect, exception:bool=False)->bool: 
    """
    Execute get status
    :args: 
        conn:rest.AnyLogConnect - Connection to AnyLog 
        exception:bool - whether to print execptions or not 
    :params: 
        status:bool
    :return: 
        stattus
    """
    status = True
    r, error = conn.get(command='get status', query=False)
    
    if errors.get_error(conn.conn, command='get status', r=r, error=error, exception=exception) == False: 
       if 'running' not in r.text or 'not' in r.text: 
           status = False
    else: 
        status = False 

    return status

def get_event_log(conn:rest.AnyLogConnect, exception:bool=False)->dict: 
    """
    Get AnyLog error log 
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :params: 
        event_log:str - content in event log
    :return: 
        data
    """
    
    r, error = conn.get(command='get event log', query=False)

    if errors.get_error(conn.conn, command='get event log', r=r, error=error, exception=exception) == False: 
        try: 
            event_log = r.text 
        except Exception as e: 
            if exception == True: 
                print('Failed to get event log from: %s (Error: %s)' % (conn, e))
            event_log = None 

    return event_log

def get_error_log(conn:rest.AnyLogConnect, exception:bool=False)->dict: 
    """
    Get AnyLog error log 
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :params: 
        error_log:str - content in error log 
    :return: 
        data
    """
    
    r, error = conn.get(command='get dictionary', query=False)

    if errors.get_error(conn.conn, command='get dictionary', r=r, error=error, exception=exception) == False: 
        try: 
            error_log = r.text 
        except Exception as e: 
            if exception == True: 
                print('Failed to get dictionary from: %s (Error: %s)' % (conn, e))
            error_log = None 

    return error_log

def get_dictionary(conn:rest.AnyLogConnect, exception:bool=False)->dict: 
    """
    Extract raw dictionary from AnyLog
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :params: 
        data:str - raw dictionary data
    :return: 
        data
    """
    
    r, error = conn.get(command='get dictionary', query=False)

    if errors.get_error(conn.conn, command='get dictionary', r=r, error=error, exception=exception) == False: 
        try: 
            data = r.text 
        except Exception as e: 
            if exception == True: 
                print('Failed to get dictionary from: %s (Error: %s)' % (conn, e))
            data = None 

    return data


def get_hostname(conn:rest.AnyLogConnect, exception:bool=False)->str: 
    """
    Extract hostname
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :params: 
        hostname:str - hostname
    :return: 
        hostname
    """
    hostname = None 
    r, error = conn.get(command='get hostname', query=False)
    if errors.get_error(conn.conn, command='get hostname', r=r, error=error, exception=exception) == False: 
        try: 
            hostname = r.text
        except Exception as e: 
            if exception == True: 
                print('Failed to extract hostname from %s (Error: %s)' % (conn.conn, e))

    return hostname

def get_processes(conn:rest.AnyLogConnect, exception:bool=False)->str: 
    """
    Get running processes 
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :params: 
        output:str - raw content from query 
    :return: 
        output 
    """
    output = None 
    r, error = conn.get(command='get processes', query=False)
    if errors.get_error(conn.conn, command='get processes', r=r, error=error, exception=exception) == False: 
        try: 
            output = r.text
        except Exception as e: 
            if exception == True: 
                print('Failed to get list of processes from %s (Error: %s)' % (conn.conn, e))
    return output 

def get_scheduler(conn:rest.AnyLogConnect, scheduler_name:str=None, exception:bool=False)->str: 
    """
    Get scheduler 
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog REST
        scheduler_name:str - name or ID of scheduled process 
        exception:bool - whether to print errors to screen 
    :params: 
        cmd:str - command to execute
        output:Str - raw content from query
    :return: 
        output
    """
    cmd='get scheduler' 
    if scheduler_name != None: 
        cmd += ' %s' % scheduler_name
    r, error = conn.get(command=cmd, query=False)
    if errors.get_error(conn.conn, command=cmd, r=r, error=error, exception=exception) == False: 
        try: 
            output = r.text
        except Exception as e: 
            if exception == True: 
                print('Failed to get information from scheduler from %s (Error: %s)' % (conn.conn, e))
    return output 


