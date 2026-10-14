import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support_logging import LevelMode, async_exec_logging
from src.core.support import ExecMode, exec_info

ANYLOG_AGENT = "AnyLog/1.23"


def _destination(remote_destination:str|None) -> dict:
    """REST header for running a command against a remote node (empty dict if not set)"""
    return {"destination": remote_destination} if remote_destination else {}


async def _validate_schedule_id(schedule_id, func_name:str) -> bool:
    """
    Check that schedule_id is a positive int
    :args:
        schedule_id - value to check
        func_name:str - calling function, for the log message
    :return:
        True if valid; otherwise logs a WARNING and returns False
        (raises TypeError / ValueError instead when FORCE_EXCEPTION is on)
    """
    # bool is a subclass of int, so exclude it explicitly
    if isinstance(schedule_id, bool) or not isinstance(schedule_id, int):
        await async_exec_logging(message=f"{func_name}: invalid data type for schedule ID "
                                         f"({type(schedule_id).__name__}) - expected int",
                                 level=LevelMode.WARNING, exception_type=TypeError)
        return False
    if schedule_id <= 0:
        await async_exec_logging(message=f"{func_name}: invalid schedule ID {schedule_id} - expected a positive int",
                                 level=LevelMode.WARNING, exception_type=ValueError)
        return False
    return True


async def _is_declared(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None) -> bool:
    """
    Whether a scheduler is already declared on the node.
    AnyLogRest errors propagate (communication failure).
    """
    result = await async_get_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                       remote_destination=remote_destination, exec_mode=ExecMode.EXECUTE)
    return f"Scheduler {schedule_id} not declared" not in str(result)


async def async_run_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                              exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Asynchronously enable a scheduler by ID
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        schedule_id:int - scheduler ID
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :return:
        response from node, or None if the ID is invalid or the scheduler is already declared
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_run_scheduler)
    if not await _validate_schedule_id(schedule_id, "run_scheduler"):
        return None
    if exec_mode == ExecMode.EXECUTE and await _is_declared(anylog_conn, schedule_id, remote_destination):
        await async_exec_logging(message=f"Scheduler {schedule_id} already declared - `run scheduler` not sent",
                                 level=LevelMode.INFO, raise_exception=False)
        return None

    headers = {
        "command": f"run scheduler {schedule_id}",
        "AnyLog-Agent": ANYLOG_AGENT,
        **_destination(remote_destination)
    }
    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def run_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                  exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_run_scheduler` - see that function for details."""
    if exec_mode == ExecMode.INFO:
        return exec_info(func=run_scheduler)
    return asyncio.run(async_run_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                           remote_destination=remote_destination, exec_mode=exec_mode))


async def async_get_scheduler(anylog_conn:AnyLogRest, schedule_id:int|None=None, remote_destination:str|None=None,
                              exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Asynchronously execute `get scheduler`
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        schedule_id:int - scheduler ID (None = all schedulers)
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :return:
        scheduler if defined else "Scheduler X not declared"; None if the ID is invalid
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_scheduler)
    if schedule_id is not None and not await _validate_schedule_id(schedule_id, "get_scheduler"):
        return None

    headers = {
        "command": f"get scheduler {schedule_id}" if schedule_id is not None else "get scheduler",
        "AnyLog-Agent": ANYLOG_AGENT,
        **_destination(remote_destination)
    }
    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def get_scheduler(anylog_conn:AnyLogRest, schedule_id:int|None=None, remote_destination:str|None=None,
                  exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_get_scheduler` - see that function for details."""
    if exec_mode == ExecMode.INFO:
        return exec_info(func=get_scheduler)
    return asyncio.run(async_get_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                           remote_destination=remote_destination, exec_mode=exec_mode))


async def async_reset_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                                exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Asynchronously reset a scheduler; declares it first if it doesn't exist yet
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        schedule_id:int - scheduler ID
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :return:
        response from node, or None if the ID is invalid
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_reset_scheduler)
    if not await _validate_schedule_id(schedule_id, "reset_scheduler"):
        return None
    if exec_mode == ExecMode.EXECUTE and not await _is_declared(anylog_conn, schedule_id, remote_destination):
        await async_exec_logging(message=f"Scheduler {schedule_id} not declared - running it before reset",
                                 level=LevelMode.INFO, raise_exception=False)
        await async_run_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                  remote_destination=remote_destination, exec_mode=exec_mode)

    headers = {
        "command": f"reset scheduler {schedule_id}",
        "AnyLog-Agent": ANYLOG_AGENT,
        **_destination(remote_destination)
    }
    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def reset_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                    exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_reset_scheduler` - see that function for details."""
    if exec_mode == ExecMode.INFO:
        return exec_info(func=reset_scheduler)
    return asyncio.run(async_reset_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                             remote_destination=remote_destination, exec_mode=exec_mode))


async def async_run_task(anylog_conn:AnyLogRest, task:str, task_name:str, task_time:str="60 seconds",
                         schedule_id:int|None=None, remote_destination:str|None=None,
                         exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Asynchronously schedule a task; declares the scheduler first if one is given and doesn't exist yet
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        task:str - actual task
        task_name:str - task name
        task_time:str - how frequently to run said task
        schedule_id:int - specific scheduler (rule engine group) to run against
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :return:
        response from node, or None if the schedule ID is invalid
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_run_task)
    if schedule_id is not None:
        if not await _validate_schedule_id(schedule_id, "run_task"):
            return None
        if exec_mode == ExecMode.EXECUTE and not await _is_declared(anylog_conn, schedule_id, remote_destination):
            await async_exec_logging(message=f"Scheduler {schedule_id} not declared - running it before "
                                             f"scheduling task '{task_name}'",
                                     level=LevelMode.INFO, raise_exception=False)
            await async_run_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                      remote_destination=remote_destination, exec_mode=exec_mode)

    scheduler_clause = f" and scheduler={schedule_id}" if schedule_id is not None else ""
    headers = {
        "command": f'schedule time="{task_time}" and name="{task_name}"{scheduler_clause} task {task}',
        "AnyLog-Agent": ANYLOG_AGENT,
        **_destination(remote_destination)
    }
    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def run_task(anylog_conn:AnyLogRest, task:str, task_name:str, task_time:str="60 seconds",
             schedule_id:int|None=None, remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_run_task` - see that function for details."""
    if exec_mode == ExecMode.INFO:
        return exec_info(func=run_task)
    return asyncio.run(async_run_task(anylog_conn=anylog_conn, task=task, task_name=task_name,
                                      task_time=task_time, schedule_id=schedule_id,
                                      remote_destination=remote_destination, exec_mode=exec_mode))


async def async_exit_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                               exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Asynchronously exit a scheduler
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        schedule_id:int - specific scheduler (rule engine group) to exit
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :return:
        response from node, or None if the ID is invalid or the scheduler isn't declared
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_exit_scheduler)
    if not await _validate_schedule_id(schedule_id, "exit_scheduler"):
        return None
    if exec_mode == ExecMode.EXECUTE and not await _is_declared(anylog_conn, schedule_id, remote_destination):
        await async_exec_logging(message=f"Scheduler {schedule_id} not declared - `exit scheduler` not sent",
                                 level=LevelMode.INFO, raise_exception=False)
        return None

    headers = {
        "command": f"exit scheduler {schedule_id}",
        "AnyLog-Agent": ANYLOG_AGENT,
        **_destination(remote_destination)
    }
    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def exit_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                   exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_exit_scheduler` - see that function for details."""
    if exec_mode == ExecMode.INFO:
        return exec_info(func=exit_scheduler)
    return asyncio.run(async_exit_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                            remote_destination=remote_destination, exec_mode=exec_mode))