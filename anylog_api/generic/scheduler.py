import re
import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.__support__ import check_interval

def run_scheduler(conn:anylog_connector.AnyLogConnector, schedule_id:int=1, destination:str=None, view_help:bool=False,
                  return_cmd:bool=False, exception:bool=False):
    """
    Declare scheduler process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/alerts%20and%20monitoring.md#adding-tasks-to-the-scheduler
    :args:
        conn:anylog_connector.AnyLogConnector - REST connecton information
        schedule_id:int - Schedule ID
        destination:str - Resmote destination ID
        view_help:bool - print information about command
        return_cmd:bool - return generated command
        exception:bool - print excptions
    :params:
        status:bool
        headers:dict - REST headers
    :return:
        status
    """
    status = None
    headers = {
        "command": f"run scheduler {schedule_id}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, headers=headers, payload=None, exception=exception)
    return status


def run_schedule_task(conn:anylog_connector.AnyLogConnector, name:str, time_interval:str, task:str, destination:str=None,
                      view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    run schedule tasks
    :args:
        conn:anylog_connector.AnyLogConnector - REST connecton information
        name:str - task name
        time_interval:str - Interval for scheduled task(s)
        task:str - actuaal task to execute
        destination:str - Resmote destination ID
        view_help:bool - print information about command
        return_cmd:bool - return generated command
        exception:bool - print excptions
    :params:
        status:bool
        headers:dict - REST headers
    :return:
        status
    """
    status = None
    headers = {
        "command": f"schedule name={name} and time={time_interval} and task {task}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    if check_interval(time_interval=time_interval, exception=exception) is False:
        return status

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, headers=headers, payload=None, exception=exception)

    return status


def get_scheduler(conn:anylog_connector.AnyLogConnector, schedule_id:int=None, destination:str=None, view_help:bool=False,
                  return_cmd:bool=False, exception:bool=False):
    """
    get running scheduler tasks
    :args:
        conn:anylog_connector.AnyLogConnector - REST connecton information
        schedule_id:int - Schedule ID
        destination:str - remote destination ID
        view_help:bool - print information about command
        return_cmd:bool - return generated command
        exception:bool - print excptions
    :params:
        status:bool
        headers:dict - REST headers
    :return:
        status
    """
    output = None
    headers = {
        "command": "get scheduler",
        "User-Agent": 'AnyLog/1.23'
    }

    if schedule_id:
        headers['command'] += f" {schedule_id}"
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output