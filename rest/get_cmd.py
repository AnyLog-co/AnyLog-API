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
import __init__
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
            if 'Scheduler Status: Not Running' in r.text:
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


def execute_query(conn:anylog_api.AnyLogConnect, dbms:str, query:str, destination='network', format:str='json', timezone:str='local',
                  include:str=None, drop:bool=False, dest:str='stdout', file:str=None, output_table:str=None)->str:
    """
    Execute Query against AnyLog
    :link:
        https://github.com/AnyLog-co/documentation/blob/master/queries.md
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        dbms:str - logical databasee name
        query:str - SELECT statement to execute
        destination:str - Whether to query remote nodes ('network') or local node ('')
        format:str - The format of the result set
            * table
            * json
        timezone:str - timezone used for time values in the result set
            * utc
            * local
        include:str - allows to treat remote tables with a different name as the table being queried
        drop:bool - drop local output table when new query starts
        dest:str - destination of result set
            * stdout
            * file
            * dbms - requires to query sql system_query "SELECT * from output_table"...
        file:str - file name for the output data
        output_table:str - table name for the output data
    :params:
        HEADER:dict - header information
        cmd:str - Query to execute
    :return:
        results from query
    :notes:
        code may move to dbms section
    """
    header = HEADER
    cmd = 'sql %s "%s"' % (dbms, query)

    """
    validate destination type
        if destination is of type file and file is not None - write results to file
        if destination is of type dbms and table is not None - write to new table 
        else: print to screen (stdout) 
    """
    if dest in ['stdout', 'file', 'dbms']:
        if dest == 'file' and file is not None:
            cmd = cmd.replace(dbms, dbms + 'dest=%s and file=%s and' % (dest, file))
        elif dest == 'dbms' and output_table is not None:
            cmd = cmd.replace(dbms, dbms + ' dest=%s and table=%s and drop=%s and ' % (dest, output_table, drop))

    if include is not None:
        cmd = cmd.replace(dbms, dbms + ' include=(%s) and extend=(@table_name as table) and ' % include)

    if timezone in ['utc', 'local']:
        cmd = cmd.replace(dbms, dbms + ' timezone=%s and ' % timezone)

    if format in ['table', 'json']:
        cmd = cmd.replace(dbms, dbms + 'format=%s and ' % format)

    if 'and "' in cmd:
        cmd = cmd.replace('and "', '"')

    header['command'] = cmd
    if destination == 'network':
        header['destination'] = 'network'

    r, error = conn.get(headers=header)
    if not other_cmd.print_error(conn=conn.conn, request_type="get", command=cmd, r=r, error=error, exception=exception):
        try:
            return r.json()
        except Exception as e:
            return r.text

