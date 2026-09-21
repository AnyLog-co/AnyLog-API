"""
The following provides configuration params
"""
import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode


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
    return asyncio.run(async_get_value(anylog_conn=anylog_conn, param_name=param_name,
                                       remote_destination=remote_destination, exec_mode=exec_mode))


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
    for key, value in kwargs.items():
        headers = {
            "command": f"set {key.lower()}={value}",
            "AnyLog-Agent": "AnyLog/1.23"
        }

        await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode)


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
    asyncio.run(async_set_var(anylog_conn=anylog_conn, exec_mode=exec_mode, **kwargs))

