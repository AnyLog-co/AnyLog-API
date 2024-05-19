from anylog_connector import AnyLogConnector
import generic_get_calls
import rest_support


def add_dict_params(anylog_conn:AnyLogConnector, content:dict, exception:bool=False):
    """
    Add parameters to dictionary
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        content:dict - key/value pairs to add to dic
        exception:bool - whether to print exceptions
    :params:
        status:bool - initially used as a list of True/False, but ultimately becomes True/False based on which has more
        headers:dict - REST header information
    :return:
        if (at least 1) fails to POST then returns False, else True
    """
    status = []
    headers = {
        'command':  None,
        'User-Agent': 'AnyLog/1.23'
    }

    for key in content:
        headers['command'] = f'set {key} = {content[key]}'
        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status.append(False)
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], exception=exception)
        elif not isinstance(r, bool):
            status.append(True)

    num_false = status.count(False)
    num_true = status.count(True)

    status = True
    if False in status:
        status = False

    return status





def run_scheduler_1(anylog_conn:AnyLogConnector, view_help:bool=False, exception:bool=False)->bool:
    """
    Execute `run scheduler 1` command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/alerts%20and%20monitoring.md#invoking-a-scheduler
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog Node
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
    :return:
        True - success
        False - fails
        None - execute `help` command
    """
    status = None
    headers = {
        'command': 'run scheduler 1',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def declare_schedule_process(anylog_conn:AnyLogConnector, time:str, task:str, start:str=None, name:str=None,
                             view_help:bool=False, exception:bool=False)->bool:
    """
    Declare new scheduled process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/alerts%20and%20monitoring.md#adding-tasks-to-the-scheduler
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        time:str - how often to run the scheduled process
        task:str - process (cmd) to run
        start:str - Scheduled start time for first execution of the task. The default value is the current day and time.
        name:str - name of the scheduled task
        view_help:bool - whether to print help information
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - print help
    :note:
        for schedule to start user needs to invoke it
    """
    status = None
    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command='schedule', exception=exception)
    else:
        command = f'schedule time={time}'
        if name is not None:
            command += f' and name="{name}"'
        if start is not None:
            command += f' and start="{start}"'
        command += f' task {task}'

        headers = {
            'command': command,
            'User-Agent': 'AnyLog/1.23'
        }

        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def run_scheduler(anylog_conn:AnyLogConnector, schedule_number:int=None, view_help:bool=False,
                  exception:bool=False)->bool:
    """
    invoke a scheduled process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/alerts%20and%20monitoring.md#invoking-a-scheduler
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        schedule_number:int - schedule number (ex `run schedule 1`
        view_help:bool - whether to print help informaton
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - print help
    """
    status=None
    headers = {
        'command': 'run scheduler',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        if schedule_number is not None:
            headers['command'] += f' {schedule_number}'

        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def set_buffer_threshold(anylog_conn:AnyLogConnector, db_name:str=None, table_name:str=None, time:str='60 seconds',
                         volume:str='10KB', write_immediate:bool=False, view_help:bool=False,
                         exception:bool=False)->bool:
    """
    Setting the buffer threshold
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#setting-and-retrieving-thresholds-for-a-streaming-mode
    :args:
        anylog_conn:AnyLogConnector - conneection to AnyLog via REST
        db_name:str - logical database name
        table_name:str - table name
        time:str - The time threshold to flush the streaming data
        volume:str - The accumulated data volume that calls the data flush process
        write_immediate:bool - Local database is immediate (independent of the calls to flush)
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - view help
    """
    status = None
    headers = {
        'command': 'set buffer threshold ',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        where_conditions = f"where time={time} and volume={volume}"

        if db_name is not None and table_name is not None:
            where_conditions = where_conditions.replace('where', f'where dbms={db_name} and table={table_name} and')
        elif db_name is not None and table_name is None:
            where_conditions = where_conditions.replace('where', f'where dbms={db_name} and')
        elif db_name is None and table_name is not None:
            where_conditions = where_conditions.replace('where', f'where table={table_name} and')
        if write_immediate is True:
            where_conditions += ' and write_immediate=true'
        else:
            where_conditions += ' and write_immediate=false'

        headers['command'] += where_conditions
        r, error = anylog_conn.post(headers=headers, payload=None)
        if r is False or int(r.status_code) != 200:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def enable_streamer(anylog_conn:AnyLogConnector, view_help:bool=False, exception:bool=False)->bool:
    """
    run streamer
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#streamer-process
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog Node
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - print help information
    """
    status = None
    headers = {
        'command': 'run streamer',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_configs, command=headers['command'], exception=exception)
    else:
        status = True
        r, error = anylog_conn.post(headers=headers)
        if r is False:
            rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status



def execute_process(anylog_conn:AnyLogConnector, file_path:str, view_help:bool=False, exception:bool=False)->bool:
    """
    Execute an AnyLog file via REST - file must be accessible on the AnyLog instance
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/node%20configuration.md#the-configuration-process
    :args:
        anylog_conn:AnyLogConnector - AnyLog connection information
        file_path:str - file (on the AnyLog instance) to be executed
        view_help:bool - whether to print help
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - print help information
    """
    status = None
    headers = {
        'command': 'process',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status