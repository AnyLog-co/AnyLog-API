"""
Node configuration - dictionary (variables), setting variables and stopping services
"""
import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, build_headers, exec_info
from src.core.support_exceptions import AnyLogError
from src.core.support_logging import LevelMode, async_exec_logging


# ---------------------------------------------------------------------------------------------------------------------
# Dictionary
# ---------------------------------------------------------------------------------------------------------------------
async def async_get_dictionary(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None,
                               exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Get the node's dictionary (AnyLog variables)
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        json_format:bool - return results in JSON format
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        get dictionary [where format=json]
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "get dictionary where format=json", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        dictionary
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_dictionary)

    headers = build_headers(command="get dictionary where format=json" if json_format else "get dictionary",
                            remote_destination=remote_destination)
    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def get_dictionary(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None,
                   exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_get_dictionary` - see that function for details"""
    return asyncio.run(async_get_dictionary(anylog_conn=anylog_conn, json_format=json_format,
                                            remote_destination=remote_destination, exec_mode=exec_mode))


async def async_get_value(anylog_conn:AnyLogRest, param_name:str|None=None, remote_destination:str|None=None,
                          exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Get a single variable from the node's dictionary
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        param_name:str - variable name; if not set, return the full dictionary
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :params:
        dictionary:dict - `get dictionary` result
    :cmd:
        get dictionary where format=json
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "get dictionary where format=json", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        value of param_name (None if not set), or the full dictionary
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_value)

    dictionary = await async_get_dictionary(anylog_conn=anylog_conn, remote_destination=remote_destination,
                                            exec_mode=exec_mode)
    if isinstance(dictionary, dict) and dictionary and param_name:
        return dictionary.get(param_name)
    return dictionary


def get_value(anylog_conn:AnyLogRest, param_name:str|None=None, remote_destination:str|None=None,
              exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_get_value` - see that function for details"""
    return asyncio.run(async_get_value(anylog_conn=anylog_conn, param_name=param_name,
                                       remote_destination=remote_destination, exec_mode=exec_mode))


async def async_set_var(anylog_conn:AnyLogRest, remote_destination:str|None=None,
                        exec_mode:ExecMode=ExecMode.EXECUTE, **kwargs):
    r"""
    Set one or more AnyLog variables - one `set` command per key
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
        kwargs - variables to set (key = variable name, lower-cased)
    :params:
        completed:list - keys already set (reported if a later key fails)
    :cmd:
        set {key}={value}
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: set node_name=anylog-operator" \
          -H "AnyLog-Agent: AnyLog/1.23"
    :return:
        list of responses, one per key
    :raise:
        ValueError - no variables given (when FORCE_EXCEPTION is on)
        AnyLogError - a `set` request failed (always re-raised, after logging what was / wasn't set)
    :sample-call:
        await async_set_var(anylog_conn=anylog_conn, param1=3, param2="hello")
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_set_var)
    if not kwargs:
        return await async_exec_logging(message="Missing key/value pairs for defining params as AnyLog variables",
                                        level=LevelMode.WARNING, exception_type=ValueError)

    responses = []
    completed = []
    for key, value in kwargs.items():
        headers = build_headers(command=f"set {key.lower()}={value}", remote_destination=remote_destination)

        if exec_mode == ExecMode.HELP:
            # help text is the same for every `set`, so only show it once
            return await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode)

        try:
            responses.append(await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode))
        except AnyLogError as error:
            remaining = [k for k in kwargs if k != key and k not in completed]
            await async_exec_logging(message=f"Failed to set '{key}' against {anylog_conn.conn} - "
                                             f"already set: {completed or 'none'}, not attempted: {remaining or 'none'}",
                                     level=LevelMode.ERROR, raise_exception=False, cause=error)
            raise   # re-raise the original AnyLogRest error unchanged

        completed.append(key)

    return responses


def set_var(anylog_conn:AnyLogRest, remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE, **kwargs):
    """Sync wrapper around `async_set_var` - see that function for details"""
    return asyncio.run(async_set_var(anylog_conn=anylog_conn, remote_destination=remote_destination,
                                     exec_mode=exec_mode, **kwargs))


# ---------------------------------------------------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------------------------------------------------
async def async_exit_service(anylog_conn:AnyLogRest, service:str, remote_destination:str|None=None,
                             exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Stop a specific service - stopping the node itself (`exit node`) isn't supported via REST
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        service:str - service to stop (ex. scheduler, operator, mqtt)
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        exit {service}
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: exit scheduler" \
          -H "AnyLog-Agent: AnyLog/1.23"
    :return:
        response from node
    :raise:
        ValueError - service is `node` (when FORCE_EXCEPTION is on)
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_exit_service)
    if service.strip().lower() == "node":
        return await async_exec_logging(message=f"'{service}' not supported for `exit` command - request not sent",
                                        level=LevelMode.WARNING, exception_type=ValueError)

    headers = build_headers(command=f"exit {service}", remote_destination=remote_destination)
    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def exit_service(anylog_conn:AnyLogRest, service:str, remote_destination:str|None=None,
                 exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_exit_service` - see that function for details"""
    return asyncio.run(async_exit_service(anylog_conn=anylog_conn, service=service,
                                          remote_destination=remote_destination, exec_mode=exec_mode))
