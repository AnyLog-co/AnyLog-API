"""
Rule engine - schedulers and the tasks that run on them
"""
import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, build_headers, exec_info
from src.core.support_logging import LevelMode, async_exec_logging


# ---------------------------------------------------------------------------------------------------------------------
# Support
# ---------------------------------------------------------------------------------------------------------------------
async def _validate_schedule_id(schedule_id, func_name:str)->bool:
    """
    Check that schedule_id is a positive int
    :args:
        schedule_id - value to check
        func_name:str - calling function, for the log message
    :return:
        True if valid; otherwise logs a WARNING and returns False
    :raise:
        TypeError / ValueError - invalid ID (when FORCE_EXCEPTION is on)
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


async def _is_declared(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None)->bool:
    """
    Whether a scheduler is already declared on the node (AnyLogRest errors propagate)
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        schedule_id:int - scheduler ID
        remote_destination:str - send the request through the connected node to another agent
    :return:
        True if declared, otherwise False
    """
    result = await async_get_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                       remote_destination=remote_destination, exec_mode=ExecMode.EXECUTE)
    return f"Scheduler {schedule_id} not declared" not in str(result)


# ---------------------------------------------------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------------------------------------------------
async def async_run_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                              exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Start a scheduler - skipped if it's already declared
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        schedule_id:int - scheduler ID
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        run scheduler {schedule_id}
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: run scheduler 1" \
          -H "AnyLog-Agent: AnyLog/1.23"
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

    headers = build_headers(command=f"run scheduler {schedule_id}", remote_destination=remote_destination)
    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def run_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                  exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_run_scheduler` - see that function for details"""
    return asyncio.run(async_run_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                           remote_destination=remote_destination, exec_mode=exec_mode))


async def async_get_scheduler(anylog_conn:AnyLogRest, schedule_id:int|None=None, remote_destination:str|None=None,
                              exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Get one scheduler, or all of them
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        schedule_id:int - scheduler ID (None = all schedulers)
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        get scheduler [{schedule_id}]
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "get scheduler 1", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        scheduler if declared, otherwise "Scheduler X not declared"; None if the ID is invalid
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_scheduler)
    if schedule_id is not None and not await _validate_schedule_id(schedule_id, "get_scheduler"):
        return None

    headers = build_headers(command=f"get scheduler {schedule_id}" if schedule_id is not None else "get scheduler",
                            remote_destination=remote_destination)
    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def get_scheduler(anylog_conn:AnyLogRest, schedule_id:int|None=None, remote_destination:str|None=None,
                  exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_get_scheduler` - see that function for details"""
    return asyncio.run(async_get_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                           remote_destination=remote_destination, exec_mode=exec_mode))


async def async_reset_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                                exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Reset a scheduler - declares it first if it doesn't exist yet
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        schedule_id:int - scheduler ID
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        reset scheduler {schedule_id}
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: reset scheduler 1" \
          -H "AnyLog-Agent: AnyLog/1.23"
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

    headers = build_headers(command=f"reset scheduler {schedule_id}", remote_destination=remote_destination)
    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def reset_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                    exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_reset_scheduler` - see that function for details"""
    return asyncio.run(async_reset_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                             remote_destination=remote_destination, exec_mode=exec_mode))


async def async_exit_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                               exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Stop a scheduler - skipped if it isn't declared
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        schedule_id:int - scheduler ID
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        exit scheduler {schedule_id}
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: exit scheduler 1" \
          -H "AnyLog-Agent: AnyLog/1.23"
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

    headers = build_headers(command=f"exit scheduler {schedule_id}", remote_destination=remote_destination)
    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def exit_scheduler(anylog_conn:AnyLogRest, schedule_id:int, remote_destination:str|None=None,
                   exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_exit_scheduler` - see that function for details"""
    return asyncio.run(async_exit_scheduler(anylog_conn=anylog_conn, schedule_id=schedule_id,
                                            remote_destination=remote_destination, exec_mode=exec_mode))


# ---------------------------------------------------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------------------------------------------------
async def async_run_task(anylog_conn:AnyLogRest, task:str, task_name:str, task_time:str="60 seconds",
                         schedule_id:int|None=None, remote_destination:str|None=None,
                         exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Schedule a task - declares the scheduler first if one is given and it doesn't exist yet
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        task:str - AnyLog command to run
        task_name:str - task name
        task_time:str - how often to run the task (ex. "60 seconds")
        schedule_id:int - scheduler (rule engine group) to run on; None = default scheduler
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        schedule time="{task_time}" and name="{task_name}" [and scheduler={schedule_id}] task {task}
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: schedule time=\"60 seconds\" and name=\"check-status\" and scheduler=1 task get status" \
          -H "AnyLog-Agent: AnyLog/1.23"
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
    headers = build_headers(command=f'schedule time="{task_time}" and name="{task_name}"{scheduler_clause} task {task}',
                            remote_destination=remote_destination)
    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def run_task(anylog_conn:AnyLogRest, task:str, task_name:str, task_time:str="60 seconds",
             schedule_id:int|None=None, remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_run_task` - see that function for details"""
    return asyncio.run(async_run_task(anylog_conn=anylog_conn, task=task, task_name=task_name,
                                      task_time=task_time, schedule_id=schedule_id,
                                      remote_destination=remote_destination, exec_mode=exec_mode))
