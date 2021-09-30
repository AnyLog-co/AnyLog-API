import __init__
import anylog_api
import errors

HEADER = {
    "command": None,
    "User-Agent": "AnyLog/1.23"
}


def get_help(conn:anylog_api.AnyLogConnect, command:str=None)->str:
    """
    Execute 'help' against AnyLog. If command is set get help regarding command
    :args: 
        conn:anylog_api.AnyLogConnect - Connection to AnyLog 
        command:str - command to get help on
    :param:
        HEADER:dict - header information
    :return:
        return help information, else None
    """
    if command is not None:
        help_stmt += " " + command

    HEADER['command'] = help_stmt

    r, error = conn.get(headers=HEADER)
    if not errors.get_error(conn=conn.conn, command=help_stmt, r=r, error=error, exception=True):
        try: 
            return r.text()
        except Exception as e:
            if exception is True:
                print('Failed to extract help information (Error: %s) ' % e)


def get_status(conn:anylog_api.AnyLogConnect, exception:bool=False)->bool: 
    """
    Execute get status
    :args: 
        conn:anylog_api.AnyLogConnect - Connection to AnyLog 
        exception:bool - whether to print execptions or not 
    :params: 
        status:bool
        HEADER:dict - header information
    :return: 
        status
    """
    status = True
    HEADER['command'] = "get status"

    r, error = conn.get(headers=HEADER)
    if not errors.get_error(conn.conn, command='get status', r=r, error=error, exception=exception):
        if 'running' not in r.text or 'not' in r.text:
            status = False
    else: 
        status = False 

    return status


def get_node_id(conn:anylog_api.AnyLogConnect, exception:bool=False)->bool:
    """
    Execute get node id
    :args:
        conn:anylog_api.AnyLogConnect - Connection to AnyLog
        exception:bool - whether to print execptions or not
    :params:
        HEADER:dict - header information
    :return:
        return node ID, else return None
    """
    HEADER['command'] = 'get node id'

    r, error = conn.get(headers=HEADER)
    if not errors.get_error(conn.conn, command='get node id', r=r, error=error, exception=exception):
        try: # if returned as JSON then ID doesn't exist
            r.json()
        except Exception as e:
            return r.text


def get_event_log(conn:anylog_api.AnyLogConnect, exception:bool=False)->str:
    """
    Get AnyLog evet log
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :params:
        HEADER:dict - header information
    :return: 
        event log, else None
    """
    HEADER['command'] = 'get event log'

    r, error = conn.get(headers=HEADER)
    if not errors.get_error(conn.conn, command='get event log', r=r, error=error, exception=exception):
        try: 
            return r.text
        except Exception as e: 
            if exception is True:
                print('Failed to get event log from: %s (Error: %s)' % (conn, e))


def get_error_log(conn:anylog_api.AnyLogConnect, exception:bool=False)->str: 
    """
    Get AnyLog error log 
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :params:
        HEADER:dict - header information
    :return: 
        return error log, else None
    """
    HEADER['command'] = 'get error log'

    r, error = conn.get(headers=HEADER)
    if not errors.get_error(conn.conn, command='get error log', r=r, error=error, exception=exception):
        try: 
            return r.text
        except Exception as e: 
            if exception is True:
                print('Failed to get error log from: %s (Error: %s)' % (conn, e))


def get_dictionary(conn:anylog_api.AnyLogConnect, exception:bool=False)->str:
    """
    Extract raw dictionary from AnyLog
    :note:
        to convert dictionary to key value pairs use: config.import_config in support/
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :params: 
        HEADER:dict - header information
    :return: 
        dictionary values
    """
    HEADER['command'] = 'get dictionary'

    r, error = conn.get(headers=HEADER)
    if not errors.get_error(conn.conn, command='get dictionary', r=r, error=error, exception=exception):
        try: 
            return r.text
        except Exception as e: 
            if exception is True:
                print('Failed to get dictionary from: %s (Error: %s)' % (conn, e))


def get_hostname(conn:anylog_api.AnyLogConnect, exception:bool=False)->str: 
    """
    Extract hostname
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :params: 
        HEADER:dict - header information
    :return: 
        hostname
    """
    HEADER['command'] = 'get hostname'
    r, error = conn.get(headers=HEADER)
    if not errors.get_error(conn.conn, command='get hostname', r=r, error=error, exception=exception):
        try: 
            return r.text
        except Exception as e: 
            if exception is True:
                print('Failed to extract hostname from %s (Error: %s)' % (conn.conn, e))


def get_processes(conn:anylog_api.AnyLogConnect, exception:bool=False)->str: 
    """
    Get running processes 
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :params: 
        HEADER:dict - header information
    :return: 
        output 
    """
    HEADER['command'] = 'get processes'

    r, error = conn.get(headers=HEADER)
    if not errors.get_error(conn.conn, command='get processes', r=r, error=error, exception=exception):
        try: 
            return r.text
        except Exception as e: 
            if exception is True:
                print('Failed to get list of processes from %s (Error: %s)' % (conn.conn, e))


def get_scheduler(conn:anylog_api.AnyLogConnect, scheduler_name:str=None, exception:bool=False)->str: 
    """
    Get scheduler 
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog REST
        scheduler_name:str - name or ID of scheduled process 
        exception:bool - whether to print errors to screen 
    :params:
        HEADER:dict - header information
        cmd:str - command to execute
        output:Str - raw content from query
    :return: 
        output
    """
    cmd='get scheduler' 
    if scheduler_name is not None:
        cmd += ' ' + scheduler_name
    HEADER['command'] = cmd

    r, error = conn.get(headers=HEADER)
    if not errors.get_error(conn.conn, command=cmd, r=r, error=error, exception=exception):
        try: 
            return r.text
        except Exception as e: 
            if exception is True:
                print('Failed to get information from scheduler from %s (Error: %s)' % (conn.conn, e))


def get_mqtt_client(conn:anylog_api.AnyLogConnect, client_id:int=None, exception:bool=False)->str: 
    """
    Get AnyLog MQTT client 
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog RESt 
        client_id:int - Specific client ID
        exception:bool - whether to print errors to screen 
    :params:
        HEADER:dict - header information
        cmd:str - Command to execute 
        mqtt_client:str - content in mqtt client
    :return: 
        mqtt client
    """
    cmd = 'run mqtt client'
    if client_id is not None:
       cmd += ' ' + client_id
    HEADER['command'] = cmd

    r, error = conn.get(headers=HEADER)
    if not errors.get_error(conn.conn, command=cmd, r=r, error=error, exception=exception):
        try: 
            return r.text
        except Exception as e: 
            if exception is True:
                print('Failed to get information regarding MQTT client from: %s (Error: %s)' % (conn, e))



