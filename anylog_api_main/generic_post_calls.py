from anylog_connector import AnyLogConnector
import generic_get_calls
import rest_support







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






