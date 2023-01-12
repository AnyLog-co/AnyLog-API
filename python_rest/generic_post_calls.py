from anylog_connection import AnyLogConnection
import support


def declare_schedule_process(anylog_conn:AnyLogConnection, time:str, task:str, name:str=None, exception:bool=False)->bool:
    """
    Declare new scheduled process
    :args:
        anylog_conn:AnyLogConnection - AnyLog REST connection information
        time:str - how often to run the scheduled process
        task:str - process (cmd) to run
        name:str - name of the scheduled task
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
    """
    status = True
    headers = {
        'command': f'schedule time={time}',
        'User-Agent': 'AnyLog/1.23',
    }
    if name == "1":
        headers['command'] = 'run scheduler 1'
    else:
        if name is not None:
            headers['command'] += f' and name={name}'
        headers += f' task {task}'

    r, error = anylog_conn.post(headers=headers, payload=None)
    if r is False or int(r.status_code) != 200:
        status = False
        if exception is True:
            support.print_rest_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def add_param(anylog_conn:AnyLogConnection, key:str, value, payload:str=None, exception:bool=False)->bool:
    """
    Add parameter to AnyLog dictionary
    :args:
        anylog_conn:AnyLogConnection - AnyLog REST connection information
        key:str - AnyLog dictionary key
        value - value associated with key
        exception:bool - whether to print exception
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
    """
    status = True
    headers = {
        'command': f'{key}={value}',
        'User-Agent': 'AnyLog/1.23'
    }

    r, error = anylog_conn.post(headers=headers, payload=payload)
    if r is False or int(r.status_code) != 200:
        status = False
        if exception is True:
            support.print_rest_error(error_type='POST', cmd=headers['command'], error=error)

    return status

def run_scheduler(anylog_conn:AnyLogConnection, schedule_number:int=None, exception:bool=False)->bool:
    """
    Execute `run scheduler`
    :args:
        anylog_conn:AnyLogConnection - AnyLog REST connection information
        schedule_number:int - schedule number (ex `run schedule 1`
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
    """
    status=True
    headers = {
        'command': 'run scheduler',
        'User-Agent': 'AnyLog/1.23'
    }
    if schedule_number is not None:
        headers['command'] += f' {schedule_number}'

    r, error = anylog_conn.post(headers=headers, payload=None)
    if r is False or int(r.status_code) != 200:
        status = False
        if exception is True:
            support.print_rest_error(error_type='POST', cmd=headers['command'], error=error)

    return status
