"""
The following are generic GET commands often used by AnyLog. Examples:
    * getting help
    * information about the node
    * logs
    * executing a query
They do not include
    * blockchain processes
    * database processes
    * authentication
"""
import import_packages
import_packages.import_dirs()
import anylog_api
import other_cmd

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
    if not other_cmd.print_error(conn=conn.conn, request_type="get", command=help_stmt, r=r, error=error, exception=True):
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
    if not other_cmd.print_error(conn=conn.conn, request_type="get", command='get status', r=r, error=error, exception=exception):
        if 'running' not in r.text or 'not' in r.text:
            status = False
    else: 
        status = False 

    return status


def get_node_id(conn:anylog_api.AnyLogConnect, exception:bool=False)->str:
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
    if not other_cmd.print_error(conn=conn.conn, request_type="get", command='get node id', r=r, error=error, exception=exception):
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
    if not other_cmd.print_error(conn=conn.conn, request_type="get", command='get event log', r=r, error=error, exception=exception):
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
    if not other_cmd.print_error(conn=conn.conn, request_type="get", command='get error log', r=r, error=error, exception=exception):
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
    if not other_cmd.print_error(conn=conn.conn, request_type="get", command='get dictionary', r=r, error=error, exception=exception):
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
    if not other_cmd.print_error(conn=conn.conn, request_type="get", command='get hostname', r=r, error=error, exception=exception):
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
    if not other_cmd.print_error(conn=conn.conn, request_type="get", command='get processes', r=r, error=error, exception=exception):
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
        cmd += ' %s' % scheduler_name
    HEADER['command'] = cmd

    r, error = conn.get(headers=HEADER)
    if not other_cmd.print_error(conn=conn.conn, request_type="get", command=cmd, r=r, error=error, exception=exception):
        try: 
            if 'Scheduler Status: Not Running' in r.text or 'Scheduler %s not declared' % scheduler_name == r.text:
                return 'not declared'
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
    if not other_cmd.print_error(conn=conn.conn, request_type="get", command=cmd, r=r, error=error, exception=exception):
        try: 
            return r.text
        except Exception as e: 
            if exception is True:
                print('Failed to get information regarding MQTT client from: %s (Error: %s)' % (conn, e))


def execute_query_print(conn:anylog_api.AnyLogConnect, dbms:str, query:str, format:str='json', stat:bool=True,
                        timezone:str='utc', include:str=None, exception:bool=False)->str:
    """
    Execute query & return the results
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/queries.md
    :args:
        conn:anylog_api.AnyLocConnect - connection to AnyLog API
        dbms:str - logical database name
        query:str - SELECT query to execute
        format:str - The format of the result set	(options: json, table)
        stat:bool - whether or not to print the statistics
        timezone:str - used for time values in the result set	local (options: utc, local)
        include:list - comma separated list of tables to query against
        exception:bool - whether or not to print exceptions
    :param:
        output = True
    """
    output = None
    header = HEADER
    header['destination'] = 'network'


    cmd = 'sql %s format=%s and stat=%s and timezone=%s' % (dbms, format, stat, timezone)

    if format not in ['json', 'table']:
        cmd.replace(format, 'json')
    if not isinstance(stat, bool):
        stat = True
        cmd.replace(stat, True)
    if timezone is not ['utc', 'local']:
        cmd.replace(timezone, 'utc')
    if include is not None:
        if isinstance(include, str):
            cmd += ' and include=%s and extend=(@table_name as table)' % tuple(include.split(','))
        elif isinstance(include, list):
            cmd += ' and include=%s and extend=(@table_name as table)' % tuple(include)
        elif isinstance(include, tuple):
            cmd += ' and include=%s and extend=(@table_name as table)' % include
    header['command'] = cmd + ' "%s"' % query

    r, error = conn.get(headers=header)
    if not other_cmd.print_error(conn=conn.conn, request_type="get", command=cmd, r=r, error=error,
                                 exception=exception):
        if stat is False:
            try:
                output = r.json()
            except Exception as e:
                stat = True

        if stat is True:
            try:
                output = r.text
            except Exception as e:
                if exception is True:
                    print("Failed to extract data for query '%s' (Error: %s)" % (cmd, e))

    return output


