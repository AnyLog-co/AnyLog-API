import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode

async def async_get_error_log(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    Asynchronized `get error log` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to node
        json_format:bool - whether to return results in JSON format
        remote_destination:str - run request against a remote node, if so provide IP and port
    :params:
        headers:dict - REST headers
        cmd:str - command to execute
    :return:
        table or JSON of error log
    """
    headers = {
        "command": f"get error log where format=json" if json_format is True else "get error log",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": remote_destination} if remote_destination else {})
    }

    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def get_error_log(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    `get error log` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to node
        json_format:bool - whether to return results in JSON format
        remote_destination:str - run request against a remote node, if so provide IP and port
    :return:
        table or JSON of error log
    """
    return asyncio.run(async_get_error_log(anylog_conn=anylog_conn, json_format=json_format,
                                           remote_destination=remote_destination, exec_mode=exec_mode))


async def async_get_event_log(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    Asynchronized `get event log` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to node
        json_format:bool - whether to return results in JSON format
        remote_destination:str - run request against a remote node, if so provide IP and port
    :params:
        headers:dict - REST headers
        cmd:str - command to execute
    :return:
        table or JSON of event log
    """
    headers = {
        "command": f"get event log where format=json" if json_format is True else "get event log",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": remote_destination} if remote_destination else {})
    }

    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def get_event_log(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    `get event log` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to node
        json_format:bool - whether to return results in JSON format
        remote_destination:str - run request against a remote node, if so provide IP and port
    :return:
        table or JSON of event log
    """
    return asyncio.run(async_get_event_log(anylog_conn=anylog_conn, json_format=json_format,
                                           remote_destination=remote_destination, exec_mode=exec_mode))

async def async_get_echo_queue(anylog_conn:AnyLogRest, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    Asynchronized `get echo queue`
    """
    headers = {
        "command": "get echo queue",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": remote_destination} if remote_destination else {})
    }

    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def get_echo_queue(anylog_conn:AnyLogRest, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    return asyncio.run(async_get_echo_queue(anylog_conn=anylog_conn, remote_destination=remote_destination, exec_mode=exec_mode))


async def async_reset_event_log(anylog_conn:AnyLogRest, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    Asynchronously  reset event logs
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :params:
        headers:dict - REST request headers
    """
    headers = {
        "command": "reset event log",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": remote_destination} if remote_destination else {})
    }
    await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def reset_event_log(anylog_conn:AnyLogRest, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    reset event logs
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :params:
        headers:dict - REST request headers
    """
    asyncio.run(async_reset_event_log(anylog_conn=anylog_conn, remote_destination=remote_destination, exec_mode=exec_mode))


async def async_reset_error_log(anylog_conn:AnyLogRest, remote_destination: str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    Asynchronously  reset error logs
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :params:
        headers:dict - REST request headers
    """
    headers = {
        "command": "reset error log",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": remote_destination} if remote_destination else {})
    }
    await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def reset_error_log(anylog_conn:AnyLogRest, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    reset error logs
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :params:
        headers:dict - REST request headers
    """
    asyncio.run(async_reset_error_log(anylog_conn=anylog_conn, remote_destination=remote_destination, exec_mode=exec_mode))



async def async_reset_echo_queue(anylog_conn:AnyLogRest, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    Asynchronously  reset echo queue logs
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :params:
        headers:dict - REST request headers
    """
    headers = {
        "command": "reset echo queue",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": remote_destination} if remote_destination else {})
    }
    await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)

def reset_echo_queue(anylog_conn: AnyLogRest, remote_destination: str | None = None, exec_mode=ExecMode.EXECUTE):
    """
    reset echo queue
    :args:
        anylog_Conn:AnyLogRest - connection to Anylog node
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :params:
        headers:dict - REST request headers
    """
    asyncio.run(async_reset_echo_queue(anylog_conn=anylog_conn, remote_destination=remote_destination, exec_mode=exec_mode))


async def async_echo_queue_state(anylog_conn:AnyLogRest, disable:bool=False, remote_destination:str|None=None,
                                 exec_mode=ExecMode.EXECUTE):
    """
    Asynchronously enable or disable echo queue
    :args:
        anylog_conn:AnyLogREST - connection to AnyLog
        disable - whether to disable echo queue
            - True: disable echo queue
            - False (default): enable echo queue
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :params:
        queue_state:str - whether on or off
            - disable == True -> off
            - disable == False -> on
        headers:dict - REST request headers
    """
    queue_state = "on"
    if disable:
        queue_state = "off"

    headers = {
        "command": f"set echo queue {queue_state}",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": remote_destination} if remote_destination else {})
    }

    await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def echo_queue_state(anylog_conn:AnyLogRest, disable:bool=False, remote_destination:str|None=None,
                     exec_mode=ExecMode.EXECUTE):
    """
    enable or disable echo queue
    :args:
        anylog_conn:AnyLogREST - connection to AnyLog
        disable - whether to disable echo queue
            - True: disable echo queue
            - False (default): enable echo queue
        remote_destination:str - remote node to execute request against
        exec_mode:ExecMode - mode to execute request
    :params:
        queue_state:str - whether on or off
            - disable == True -> off
            - disable == False -> on
        headers:dict - REST request headers
    """
    asyncio.run(async_echo_queue_state(anylog_conn=anylog_conn, disable=disable, remote_destination=remote_destination,
                                       exec_mode=exec_mode))
