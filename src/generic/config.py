"""
The following provides configuration params
"""
import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, exec_info

from src.core.support_exceptions import AnyLogError
from src.core.support_logging import LevelMode, async_exec_logging


async def async_get_dictionary(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None,
                               exec_mode=ExecMode.EXECUTE):
    """
    Execute `get dictionary` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        json_format:bool - return data in JSON format
        remote_destination:str - remote destination
        exec_mode - type of execution request
    :params;
        headers:dict - REST headers
    :return:
        dictionary
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_dictionary)

    headers = {
        "command": "get dictionary where format=json" if json_format else "get dictionary",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": remote_destination} if remote_destination else {})
    }

    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)

def get_dictionary(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None,
                   exec_mode=ExecMode.EXECUTE):
    """
    Execute `get dictionary` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        json_format:bool - return data in JSON format
        remote_destination:str - remote destination
        exec_mode - type of execution request
    :params;
        headers:dict - REST headers
    :return:
        dictionary
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=get_dictionary)

    return asyncio.run(async_get_dictionary(anylog_conn=anylog_conn, json_format=json_format,
                                            remote_destination=remote_destination, exec_mode=exec_mode))

async def async_get_value(anylog_conn:AnyLogRest, param_name:str|None=None, remote_destination:str|None=None,
                           exec_mode=ExecMode.EXECUTE):
    """
    Execute `get dictionary` to extract a specific param
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        param_name:str - param to check against. if not provided return full dict
        remote_destination:str - remote destination
        exec_mode - type of execution request
    :params;
        headers:dict - REST headers
        dictionary:dict - result from `get dict` request
    :return:
        value associated with param
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_value)

    dictionary = await async_get_dictionary(anylog_conn=anylog_conn, remote_destination=remote_destination,
                                            exec_mode=exec_mode)

    if (dictionary and isinstance(dictionary, dict)) and param_name:
        return dictionary.get(param_name)

    return dictionary


def get_value(anylog_conn:AnyLogRest, param_name:str|None=None, remote_destination:str|None=None,
              exec_mode=ExecMode.EXECUTE):
    """
    Execute `get dictionary` to extract a specific param
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        param_name:str - param to check against. if not provided return full dict
        remote_destination:str - remote destination
        exec_mode - type of execution request
    :params;
        headers:dict - REST headers
    :return:
        value associated with param
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=get_value)

    return asyncio.run(async_get_value(anylog_conn=anylog_conn, param_name=param_name,
                                       remote_destination=remote_destination, exec_mode=exec_mode))

async def async_exit_service(anylog_conn:AnyLogRest, service:str, exec_mode=ExecMode.EXECUTE):
    """
    Execute an `exit` command on a specific service - not supported 2x remote or taking down the actual node
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        service:str - Service to stop
        exec_mode - type of execution request
    :params:
        headers:dict - REST request headers
    :raise:
        ValueError: if user attempts to exit node via REST
    """
    if service.strip().lower() == "node":
        return await async_exec_logging(message=f"'{service}' not supported for `exit` command - request not sent",
                                        level=LevelMode.WARNING, exception_type=ValueError)
    elif exec_mode == ExecMode.INFO:
        return exec_info(func=async_exit_service)

    headers = {
        "command": f"exit {service}",
        "AnyLog-Agent": "AnyLog/1.23"
    }
    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)

def exit_service(anylog_conn:AnyLogRest, service:str, exec_mode=ExecMode.EXECUTE):
    """
    Execute an `exit` command on a specific service - not supported 2x remote or taking down the actual node
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        service:str - Service to stop
        exec_mode - type of execution request
    :params:
        headers:dict - REST request headers
    :raise:
        ValueError: if user attempts to exit node via REST
    """
    if service.strip().lower() == "node":
        return asyncio.run(async_exec_logging(message=f"'{service}' not supported for `exit` command - request not sent",
                                        level=LevelMode.WARNING, exception_type=ValueError))

    elif exec_mode == ExecMode.INFO:
        return exec_info(func=exit_service)

    return asyncio.run(async_exit_service(anylog_conn=anylog_conn, service=service, exec_mode=exec_mode))


async def async_set_var(anylog_conn:AnyLogRest, exec_mode=ExecMode.EXECUTE, **kwargs):
    """
    Asynchronously  set env variable
    :sample call:
        async_set_var(anylog_conn=anylog_conn, exec_mode=exec_mode, param1=3, param2="hello")
    :aegs:
        anylog_conn:AnyLogRest - connection to Anylog node
        exec_mode - execution mode
    :params:
        headers:dict - REST headers
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_set_var)

    if not kwargs:
        return await async_exec_logging(message="Missing key/value pairs for defining params as AnyLog variables",
                                        level=LevelMode.WARNING, exception_type=ValueError)

    responses = []
    completed = []
    for key, value in kwargs.items():
        headers = {
            "command": f"set {key.lower()}={value}",
            "AnyLog-Agent": "AnyLog/1.23"
        }

        if exec_mode == ExecMode.HELP:
            # help text is the same for every `set`, so only show it once
            return await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode)

        try:
            responses.append(await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode))
        except AnyLogError as error:
            remaining = [k for k in kwargs if k != key and k not in completed]
            await async_exec_logging(
                message=f"Failed to set '{key}' against {anylog_conn.conn} - "
                        f"already set: {completed or 'none'}, not attempted: {remaining or 'none'}",
                level=LevelMode.ERROR, raise_exception=False, cause=error)
            raise  # re-raise the original AnyLogRest error unchanged

        completed.append(key)

    return responses


def set_var(anylog_conn:AnyLogRest, exec_mode=ExecMode.EXECUTE, **kwargs):
    """
    set env variable
    :sample call:
        async_set_var(anylog_conn=anylog_conn, exec_mode=exec_mode, param1=3, param2="hello")
    :aegs:
        anylog_conn:AnyLogRest - connection to Anylog node
        exec_mode - execution mode
    :params:
        headers:dict - REST headers
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=set_var)

    return asyncio.run(async_set_var(anylog_conn=anylog_conn, exec_mode=exec_mode, **kwargs))
    
