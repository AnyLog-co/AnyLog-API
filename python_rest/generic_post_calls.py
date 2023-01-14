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
        'command': 'set %s = %s',
        'User-Agent': 'AnyLog/1.23'
    }

    for key in content:
        headers['command'] = headers['command'] % (key, content[key])
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


def network_connect(anylog_conn:AnyLogConnector, conn_type:str, internal_ip:str, internal_port:int,
                    external_ip:str=None, external_port:int=None, bind:bool=True, threads:int=3, rest_timeout:int=30,
                    view_help:bool=False, exception:bool=False)->bool:
    """
    Connect to a network
    :args: 
        anylog_conn:AnyLogConnector - connecton to AnyLog 
        conn_type:str - connection type (TCP, REST, broker)
        internal_ip:str - internal/local  ip
        internal_port  - internal/local ip
        external_ip:str - external ip
        external_port:str - external port
        bind:bool - whether to bind or not
        threads:int - number of threads 
        rest_timeout:bool - REST timeout 
        view_help:bool - whether to print help information
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
    # validate
    status = False
    if conn_type.upper() == 'TCP' or conn_type.upper() == 'REST' or  conn_type.lower() == 'broker':
        status = None
    else:
        if exception is True:
            print(f'Invalid connection type: {conn_type}. Cannot execute connection')
        return status

    headers = {
        'command': rest_support.generate_connection_command(conn_type=conn_type, internal_ip=internal_ip,
                                                       internal_port=internal_port, external_ip=external_ip,
                                                       external_port=external_port, bind=bind, threads=threads,
                                                       rest_timeout=rest_timeout),
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




def declare_schedule_process(anylog_conn:AnyLogConnector, time:str, task:str, name:str=None, exception:bool=False)->bool:
    """
    Declare new scheduled process
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
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


def add_param(anylog_conn:AnyLogConnector, key:str, value, payload:str=None, exception:bool=False)->bool:
    """
    Add parameter to AnyLog dictionary
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
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

def run_scheduler(anylog_conn:AnyLogConnector, schedule_number:int=None, exception:bool=False)->bool:
    """
    Execute `run scheduler`
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
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
