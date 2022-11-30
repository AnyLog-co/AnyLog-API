import json
from anylog_connection import AnyLogConnection
from support import print_error


def network_connection(anylog_conn:AnyLogConnection, connection_type:str, external_ip:str=None, local_ip:str=None,
                       port:int=2048, threads:int=6, timeout:int=30, ssl:bool=False, exception:bool=False):
    """
    Connect to TCP, REST or Message Broker
    :urls:
        TCP: https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#the-tcp-server-process
        REST: https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#rest-requests
        Message Broker: https://github.com/AnyLog-co/documentation/blob/master/message%20broker.md#configuring-an-anylog-node-as-a-message-broker
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        connection_type:str - connection type
            - tcp
            - rest
            - message broker
        external_ip:str - external IP
        local_ip:str - local IP
        port:int - connection port
        threads:int - optional parameter for the number of workers threads that process requests which are send to the provided IP and Port.
        timeout:int - REST timeout
        ssl:bool - Max wait time in seconds
        exception:bool - whether to print exception
    :params:
        status:bool
        headers:dict - REST header
    :return:
        status
    """
    status = True
    headers ={
        "command": "",
        "User-Agent": "AnyLog/1.23"
    }
    if connection_type == 'tcp':
        headers['command'] = f'run tcp server {external_ip} {port} {local_ip} {port} {threads}'
    elif connection_type == 'rest':
        headers['command'] = f'run rest server {local_ip} {port} where timeout={timeout} and threads={threads} and ssl={str(ssl).lower()}'
    elif connection_type == 'message broker':
        headers['command'] = f'run message broker {external_ip} {port} {local_ip} {port} {threads}'

    r, error = anylog_conn.post(headers=headers)
    if exception is True and r is False:
        print_error(error_type='POST', cmd=headers['command'], error=error)
        status = False
    return status


def schedule_task(anylog_conn:AnyLogConnection, name:str, time:str=None, task=None, exception:bool=False)->bool:
    """
    Run Scheduler
        if name == 1 then "run scheduler 1"
        else schedule {time} and {name} and {task}
    :url:
        Invoking scheduler: https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#scheduler-process
        Alert & Monitoring: https://github.com/AnyLog-co/documentation/blob/master/alerts%20and%20monitoring.md#alerts-and-monitoring
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        name:str - task name
        time:str - how often to run the task
        task:str - The actual task to run
        exception:bool - whether to print exception
    :params:
        status:bool
        headers:dict - REST header
    :return:
        status
    """
    status = True
    headers = {
        "command": "",
        "User-Agent": "AnyLog/1.23"
    }

    if name == 1 or name == "1":
        headers['command'] = "run scheduler 1"
    else:
        headers['command'] = f"schedule name={name} and time={time} and task {task}"

    r, error = anylog_conn.post(headers=headers)
    if exception is True and r is False:
        print_error(error_type='POST', cmd=headers['command'], error=error)
        status = False

    return status


