"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import warnings
from sched import scheduler
from typing import Union

from pkg_resources import find_nothing

import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.__support__ import check_interval


def run_scheduler(conn:anylog_connector.AnyLogConnector, schedule_id:int=1, destination:str=None, view_help:bool=False,
                  return_cmd:bool=False, exception:bool=False)->Union[None, str, bool]:
    """
    Declare scheduler process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/alerts%20and%20monitoring.md#adding-tasks-to-the-scheduler
    :args:
        conn:anylog_connector.AnyLogConnector - REST connection information
        schedule_id:int - Schedule ID
        destination:str - remote destination ID
        view_help:bool - print information about command
        return_cmd:bool - return generated command
        exception:bool - print exception
    :params:
        status:bool
        headers:dict - REST headers
    :return:
        if invalid schedule ID - raise error with exception, without exception returns None
        if returnn_cmd is True - returns generated command
        else
            True -> success
            False -> fails
    """
    is_invalid = False
    if not schedule_id:
        is_invalid = True
        if exception is True:
            raise KeyError(f"Missing schedule ID, cannot start new scheduler process")
    else:
        try:
            schedule_id = int(schedule_id)
        except ValueError as error:
            is_invalid = True
            if exception is True:
                raise ValueError(f"Invalid schedule ID, must be an int greater than 0 (Error {error})")
        if schedule_id <= 0:
            is_invalid = True
            if exception is True:
                raise ValueError(f"Invalid schedule ID, must be an int greater than 0")

    if is_invalid:
        return None  # If invalid, return None (or raise error if exception=False)

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
    else:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)
    return status


def run_schedule_task(conn:anylog_connector.AnyLogConnector, name:str, time_interval:str, task:str, destination:str=None,
                      view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[None, str, bool]:
    """
    run schedule tasks
    :args:
        conn:anylog_connector.AnyLogConnector - REST connection information
        name:str - task name
        time_interval:str - Interval for scheduled task(s)
        task:str - actual task to execute
        destination:str - remote destination ID
        view_help:bool - print information about command
        return_cmd:bool - return generated command
        exception:bool - print exception
    :params:
        output
        headers:dict - REST headers
    :return:
        if invalid interval - raise Error
        if return_cmd -> returns generated command
        else ->
            - True: success
            - False: fails
    """
    if not check_interval(time_interval=time_interval, exception=exception):
        if exception is True:
            raise ValueError('Invalid time interval for schedule process. Support time intervals: second(s), minute(s), hour(s), day(s), month(s)')
        return None

    headers = {
        "command": f"schedule name={name} and time={time_interval} and task {task}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    if check_interval(time_interval=time_interval, exception=exception) is False:
        if exception is True:
            raise ValueError(f'Time interval value is in valid. Support intervals: second, minute, hour, day, month, year')

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = execute_publish_cmd(conn=conn, cmd="POST", headers=headers, payload=None, exception=exception)

    return output


def get_scheduler(conn:anylog_connector.AnyLogConnector, schedule_id:int=None, destination:str=None, view_help:bool=False,
                  return_cmd:bool=False, exception:bool=False)->Union[None, str]:
    """
    get running scheduler tasks
    :args:
        conn:anylog_connector.AnyLogConnector - REST connection information
        schedule_id:int - Schedule ID
        destination:str - remote destination ID
        view_help:bool - print information about command
        return_cmd:bool - return generated command
        exception:bool - print exception
    :params:
        output
        headers:dict - REST headers
    :return:
        status
    """
    is_invalid = False
    try:
        if schedule_id and not int(schedule_id):
            is_invalid = True
            if exception is True:
                raise ValueError("Missing or invalid schedule ID, must be an int great than 0")
    except KeyError as error:
        is_invalid = True
        if exception is True:
            raise KeyError(f"Invalid schedule ID, must be an int greater than 0 (Error {error})")
    except ValueError as error:
        is_invalid = True
        if exception is True:
            raise ValueError(f"Invalid schedule ID, must be an int greater than 0 (Error {error})")
    finally:
        if is_invalid is True and exception is True:
            warnings.warn(f'Invalid schedule ID, will be ignored when getting schedule information')

    headers = {
        "command": "get scheduler",
        "User-Agent": 'AnyLog/1.23'
    }

    if schedule_id and is_invalid is False:
        headers['command'] += f" {int(schedule_id)}"

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output