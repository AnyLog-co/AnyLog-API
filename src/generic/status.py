"""
The following provides functions that check the state of the node and whether it is able to communicate with
other nodes in the network.
"""

import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, exec_info

async def async_get_processes(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None,
                              exec_mode=ExecMode.EXECUTE):
    """
    Asynchronized `get process` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to node
        json_format:bool - whether to return results in JSON format
        remote_destination:str - run request against a remote node, if so provide IP and port
    :params:
        headers:dict - REST headers
    :return:
        table or JSON of node processes
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_processes)

    headers = {
        "command": "get processes where format=json" if json_format else "get processes",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": remote_destination} if remote_destination else {})
    }

    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)

def get_processes(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    Synchronized `get process` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to node
        json_format:bool - whether to return results in JSON format
        remote_destination:str - run request against a remote node, if so provide IP and port
    :params:
        headers:dict - REST headers
    :return:
        table or JSON of node processes
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=get_processes)

    return asyncio.run(async_get_processes(anylog_conn=anylog_conn, json_format=json_format,
                                           remote_destination=remote_destination, exec_mode=exec_mode))


async def async_get_status(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    Asynchronized `get status` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to node
        json_format:bool - whether to return results in JSON format
        remote_destination:str - run request against a remote node, if so provide IP and port
    :params:
        headers:dict - REST headers
    :return:
        node status
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_status)

    headers = {
        "command": "get status where format=json" if json_format else "get status",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": remote_destination} if remote_destination else {})
    }

    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)

def get_status(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    `get status` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to node
        json_format:bool - whether to return results in JSON format
        remote_destination:str - run request against a remote node, if so provide IP and port
    :params:
        headers:dict - REST headers
    :return:
        node status
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=get_status)

    return asyncio.run(async_get_status(anylog_conn=anylog_conn, json_format=json_format,
                                        remote_destination=remote_destination, exec_mode=exec_mode))


async def async_test_node(anylog_conn:AnyLogRest, exec_mode=ExecMode.EXECUTE):
    """
    Asynchronized `test node` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to node
    :params:
        headers:dict - REST headers
    :return:
        node status
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_test_node)

    headers = {
        "command": "test node",
        "AnyLog-Agent": "AnyLog/1.23"
    }

    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def test_node(anylog_conn:AnyLogRest, exec_mode=ExecMode.EXECUTE):
    """
    `test node` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to node
    :params:
        headers:dict - REST headers
    :return;
        node status
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=test_node)

    return asyncio.run(async_test_node(anylog_conn=anylog_conn, exec_mode=exec_mode))


async def async_test_network(anylog_conn:AnyLogRest, exec_mode=ExecMode.EXECUTE):
    """
    Asynchronized `test network` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to node
    :params:
        headers:dict - REST headers
    :return;
        network communication status
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_test_network)

    headers = {
        "command": "test network",
        "AnyLog-Agent": "AnyLog/1.23"
    }

    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def test_network(anylog_conn:AnyLogRest, exec_mode=ExecMode.EXECUTE):
    """
    `test network` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to node
    :params:
        headers:dict - REST headers
    :return;
        network communication status
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=test_network)

    return asyncio.run(async_test_network(anylog_conn=anylog_conn, exec_mode=exec_mode))
