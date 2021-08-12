import __init__
import rest.anylog_api as anylog_api

import support.errors as errors

def get_help(conn:anylog_api.AnyLogConnect, command:str=None): 
    """
    Execute 'help' against AnyLog. If command is set get help regarding command
    :args: 
        conn:anylog_api.AnyLogConnect - Connection to AnyLog 
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

def get_status(conn:anylog_api.AnyLogConnect, exception:bool=False)->bool: 
    """
    Execute get status
    :args: 
        conn:anylog_api.AnyLogConnect - Connection to AnyLog 
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

def get_event_log(conn:anylog_api.AnyLogConnect, exception:bool=False)->str:
    """
    Get AnyLog error log 
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :params: 
        event_log:str - content in event log
    :return: 
        event_log
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

def get_error_log(conn:anylog_api.AnyLogConnect, exception:bool=False)->str: 
    """
    Get AnyLog error log 
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :params: 
        error_log:str - content in error log 
    :return: 
        error_log
    """
    
    r, error = conn.get(command='get error log', query=False)

    if errors.get_error(conn.conn, command='get error log', r=r, error=error, exception=exception) == False: 
        try: 
            error_log = r.text 
        except Exception as e: 
            if exception == True: 
                print('Failed to get error log from: %s (Error: %s)' % (conn, e))
            error_log = None 

    return error_log

def get_dictionary(conn:anylog_api.AnyLogConnect, exception:bool=False)->dict: 
    """
    Extract raw dictionary from AnyLog
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog RESt 
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


def get_hostname(conn:anylog_api.AnyLogConnect, exception:bool=False)->str: 
    """
    Extract hostname
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog RESt 
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

def get_processes(conn:anylog_api.AnyLogConnect, exception:bool=False)->str: 
    """
    Get running processes 
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog RESt 
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

def get_scheduler(conn:anylog_api.AnyLogConnect, scheduler_name:str=None, exception:bool=False)->str: 
    """
    Get scheduler 
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog REST
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

def get_mqtt_client(conn:anylog_api.AnyLogConnect, client_id:int=None, exception:bool=False)->str: 
    """
    Get AnyLog MQTT client 
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog RESt 
        client_id:int - Specific client ID
        exception:bool - whether to print errors to screen 
    :params: 
        cmd:str - Command to execute 
        mqtt_client:str - content in mqtt client
    :return: 
        mqtt client
    """
    cmd = 'run mqtt client'
    if client_id != None: 
       cmd += ' %s' % client_id

    r, error = conn.get(command=cmd, query=False)
    if errors.get_error(conn.conn, command=cmd, r=r, error=error, exception=exception) == False: 
        try: 
            mqtt_client = r.text 
        except Exception as e: 
            if exception == True: 
                print('Failed to get information regarding MQTT client from: %s (Error: %s)' % (conn, e))
            error_log = None 

    return mqtt_client


