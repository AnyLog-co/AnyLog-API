"""
Node logs - error log, event log and echo queue
"""
import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, build_headers, exec_info


# ---------------------------------------------------------------------------------------------------------------------
# Error / event log
# ---------------------------------------------------------------------------------------------------------------------
async def async_get_error_log(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None,
                              exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Get the node's error log
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        json_format:bool - return results in JSON format
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        get error log [where format=json]
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "get error log where format=json", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        table or JSON of the error log
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_error_log)

    headers = build_headers(command="get error log where format=json" if json_format else "get error log",
                            remote_destination=remote_destination)
    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def get_error_log(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None,
                  exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_get_error_log` - see that function for details"""
    return asyncio.run(async_get_error_log(anylog_conn=anylog_conn, json_format=json_format,
                                           remote_destination=remote_destination, exec_mode=exec_mode))


async def async_get_event_log(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None,
                              exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Get the node's event log
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        json_format:bool - return results in JSON format
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        get event log [where format=json]
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "get event log where format=json", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        table or JSON of the event log
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_event_log)

    headers = build_headers(command="get event log where format=json" if json_format else "get event log",
                            remote_destination=remote_destination)
    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def get_event_log(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None,
                  exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_get_event_log` - see that function for details"""
    return asyncio.run(async_get_event_log(anylog_conn=anylog_conn, json_format=json_format,
                                           remote_destination=remote_destination, exec_mode=exec_mode))


async def async_reset_error_log(anylog_conn:AnyLogRest, remote_destination:str|None=None,
                                exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Clear the node's error log
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        reset error log
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: reset error log" \
          -H "AnyLog-Agent: AnyLog/1.23"
    :return:
        response from node
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_reset_error_log)

    headers = build_headers(command="reset error log", remote_destination=remote_destination)
    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def reset_error_log(anylog_conn:AnyLogRest, remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_reset_error_log` - see that function for details"""
    return asyncio.run(async_reset_error_log(anylog_conn=anylog_conn, remote_destination=remote_destination,
                                             exec_mode=exec_mode))


async def async_reset_event_log(anylog_conn:AnyLogRest, remote_destination:str|None=None,
                                exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Clear the node's event log
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        reset event log
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: reset event log" \
          -H "AnyLog-Agent: AnyLog/1.23"
    :return:
        response from node
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_reset_event_log)

    headers = build_headers(command="reset event log", remote_destination=remote_destination)
    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def reset_event_log(anylog_conn:AnyLogRest, remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_reset_event_log` - see that function for details"""
    return asyncio.run(async_reset_event_log(anylog_conn=anylog_conn, remote_destination=remote_destination,
                                             exec_mode=exec_mode))


# ---------------------------------------------------------------------------------------------------------------------
# Echo queue
# ---------------------------------------------------------------------------------------------------------------------
async def async_get_echo_queue(anylog_conn:AnyLogRest, remote_destination:str|None=None,
                               exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Get the node's echo queue
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        get echo queue
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "get echo queue", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        echo queue content
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_echo_queue)

    headers = build_headers(command="get echo queue", remote_destination=remote_destination)
    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def get_echo_queue(anylog_conn:AnyLogRest, remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_get_echo_queue` - see that function for details"""
    return asyncio.run(async_get_echo_queue(anylog_conn=anylog_conn, remote_destination=remote_destination,
                                            exec_mode=exec_mode))


async def async_reset_echo_queue(anylog_conn:AnyLogRest, remote_destination:str|None=None,
                                 exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Clear the node's echo queue
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        reset echo queue
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: reset echo queue" \
          -H "AnyLog-Agent: AnyLog/1.23"
    :return:
        response from node
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_reset_echo_queue)

    headers = build_headers(command="reset echo queue", remote_destination=remote_destination)
    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def reset_echo_queue(anylog_conn:AnyLogRest, remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_reset_echo_queue` - see that function for details"""
    return asyncio.run(async_reset_echo_queue(anylog_conn=anylog_conn, remote_destination=remote_destination,
                                              exec_mode=exec_mode))


async def async_echo_queue_state(anylog_conn:AnyLogRest, disable:bool=False, remote_destination:str|None=None,
                                 exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Enable or disable the echo queue
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        disable:bool - True disables the echo queue, False (default) enables it
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :params:
        queue_state:str - "off" when disable is True, otherwise "on"
    :cmd:
        set echo queue [on|off]
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: set echo queue on" \
          -H "AnyLog-Agent: AnyLog/1.23"
    :return:
        response from node
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_echo_queue_state)

    queue_state = "off" if disable else "on"
    headers = build_headers(command=f"set echo queue {queue_state}", remote_destination=remote_destination)
    return await anylog_conn.async_post(headers=headers, exec_mode=exec_mode)


def echo_queue_state(anylog_conn:AnyLogRest, disable:bool=False, remote_destination:str|None=None,
                     exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_echo_queue_state` - see that function for details"""
    return asyncio.run(async_echo_queue_state(anylog_conn=anylog_conn, disable=disable,
                                              remote_destination=remote_destination, exec_mode=exec_mode))
