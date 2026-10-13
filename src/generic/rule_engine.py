import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, exec_info
from src.generic.config import async_exit_service

async def async_run_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                              exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Asynchronously enable a scheduler by ID
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        scheduler_id:int - scheduler ID
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :params:
        headers:dict - REST headers
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_run_scheduler)
    elif isinstance(schedule_id, int) and schedule_id == 0:
        raise ValueError(f"Invalid schedule ID: {schedule_id}")
    elif not isinstance(schedule_id, int):
        raise TypeError(f"Invalid data type for schedule ID - expected type int")
    elif exec_mode == ExecMode.EXECUTE:
        is_scheduler = await async_get_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                                 remote_destination=remote_destination, exec_mode=exec_mode)
        # if schedule already exists return None
        if is_scheduler.strip() == f"Scheduler {schedule_id} not declared":
            return None

    headers = {
        "command": f"run scheduler {schedule_id}",
        "AnyLog-Agent": "AnyLog/1.23",
        **{{"destination": remote_destination} if remote_destination else {}}
    }

    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def run_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                  exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    enable a scheduler by ID
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        scheduler_id:int - scheduler ID
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :params:
        headers:dict - REST headers
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=run_scheduler)
    elif isinstance(schedule_id, int) and schedule_id == 0:
        raise ValueError(f"Invalid schedule ID: {schedule_id}")
    elif not isinstance(schedule_id, int):
        raise TypeError(f"Invalid data type for schedule ID - expected type int")

    return asyncio.run(async_run_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                           remote_destination=remote_destination, exec_mode=exec_mode))


async def async_get_scheduler(anylog_conn:AnyLogRest, schedule_id:int=None, remote_destination:str|None=None,
                              exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Asynchronously execute `get scheduler`
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        scheduler_id:int - scheduler ID
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :params:
        payload:dict -> str: command to execute
    :return;
        scheduler if defined else "Scheduler X not declared"
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_scheduler)

    payload = {
        "command": f"get scheduler {schedule_id}" if schedule_id else "get scheduler",
        "AnyLog-Agent": "AnyLog/1.23",
        **{{"destination": remote_destination} if remote_destination else {}}
    }

    return anylog_conn.async_post(headers={"Content-Type": "application/json"}, payload=json.dumps(payload),
                                  exec_mode=exec_mode)


def get_scheduler(anylog_conn:AnyLogRest, schedule_id:int=None, remote_destination:str|None=None,
                        exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    execute `get scheduler`
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        scheduler_id:int - scheduler ID
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :params:
        payload:dict -> str: command to execute
    :return;
        scheduler if defined else "Scheduler X not declared"
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=get_scheduler)


    return asyncio.run(async_get_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                           remote_destination=remote_destination, exec_mode=exec_mode))


async def async_reset_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                                exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Asynchronously run command to reset the scheduler
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        scheduler_id:int - scheduler ID
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :params:
        is_scheduler:str - based on scheduler ID check whether the scheduler already
        headers:dict - REST call headers
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_reset_scheduler)
    elif isinstance(schedule_id, int) and schedule_id == 0:
        raise ValueError(f"Invalid schedule ID: {schedule_id}")
    elif not isinstance(schedule_id, int):
        raise TypeError(f"Invalid data type for schedule ID - expected type int")
    elif schedule_id and exec_mode == ExecMode.EXECUTE:
        is_scheduler = await async_get_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                                 remote_destination=remote_destination, exec_mode=exec_mode)
        if is_scheduler.strip() == f"Scheduler {schedule_id} not declared":
            await async_run_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                      remote_destination=remote_destination, exec_mode=exec_mode)

    headers = {
        "command": f"reset scheduler {schedule_id}",
        "AnyLog-Agent": "AnyLog/1.23",
        **{{"destination": remote_destination} if remote_destination else {}}
    }

    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def reset_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                    exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    run command to reset the scheduler
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        scheduler_id:int - scheduler ID
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :params:
        is_scheduler:str - based on scheduler ID check whether the scheduler already
        headers:dict - REST call headers
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=reset_scheduler)

    return asyncio.run(async_reset_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                             remote_destination=remote_destination, exec_mode=exec_mode))


async def async_run_task(anylog_conn:AnyLogRest, task:str, task_name:str, task_time:str="60 seconds",
                         schedule_id:int|None=None, remote_destination:str|None=None,
                         exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Initiate a task using async process via REST
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        task:str - actual task
        task_name:str - task name
        task_time:str - how frequently to run said task
        schedule_id:int - specific scheduler (rule engine group) to run against
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    """
    command = f'schedule time="{task_time}" and name="{task_name}" {f"and scheduler={schedule_id}" if schedule_id else ""} task {task}'

    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_reset_scheduler)
    elif schedule_id and not isinstance(schedule_id, int):
        raise TypeError(f"Invalid data type for schedule ID - expected type int")
    elif schedule_id and exec_mode == ExecMode.EXECUTE:
        is_scheduler = await async_get_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                                 remote_destination=remote_destination, exec_mode=exec_mode)
        if is_scheduler.strip() == f"Scheduler {schedule_id} not declared":
            await async_run_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                      remote_destination=remote_destination, exec_mode=exec_mode)

    headers = {
        "command": command,
        "AnyLog-Agent": "AnyLog/1.23",
        **{{"destination": remote_destination} if remote_destination else {}}
    }

    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)

def run_task(anylog_conn:AnyLogRest, task:str, task_name:str, task_time:str="60 seconds", schedule_id:int|None=None,
             remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Initiate a task process via REST
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        task:str - actual task
        task_name:str - task name
        task_time:str - how frequently to run said task
        schedule_id:int - specific scheduler (rule engine group) to run against
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    """

    if exec_mode == ExecMode.INFO:
        return exec_info(func=reset_scheduler)
    elif schedule_id and not isinstance(schedule_id, int):
        raise TypeError(f"Invalid data type for schedule ID - expected type int")

    return asyncio.run(async_run_task(anylog_conn=anylog_conn, task=task, task_name=task_name, task_time=task_time,
                                      schedule_id=schedule_id, remote_destination=remote_destination, exec_mode=exec_mode))

async def async_exit_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None,
                               exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Asynchronously exit a scheduler
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        schedule_id:int - specific scheduler (rule engine group) to run against
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_exit_scheduler)
    elif schedule_id and not isinstance(schedule_id, int):
        raise TypeError(f"Invalid data type for schedule ID - expected type int")
    elif exec_mode == ExecMode.EXECUTE:
        is_scheduler = await async_get_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                                 remote_destination=remote_destination, exec_mode=exec_mode)
        if is_scheduler.strip() == f"Scheduler {schedule_id} not declared":
            return None

    headers = {
        "command": f"exit scheduler {schedule_id}",
        "AnyLog-Agent": "AnyLog/1.23",
        **{{"destination": remote_destination} if remote_destination else {}}
    }

    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def exit_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None,
                   exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    exit a scheduler
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        schedule_id:int - specific scheduler (rule engine group) to run against
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=exit_scheduler)

    return asyncio.run(async_exit_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                            remote_destination=remote_destination, exec_mode=exec_mode))


