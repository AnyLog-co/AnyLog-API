"""
The following provides functions that check the state of the node and whether it is able to communicate with
other nodes in the network.
"""

import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, exec_info
from src.core.support_logging import LevelMode, async_exec_logging

SERVICE_ALIASES = {
    "blockchain": "Blockchain Sync",
    "blobs": "Blobs Archiver",
    "msg client": "MSG Client Pool",
    "uns": "UNS Streamer",
    "kafka": "Kafka Consumer",
    "plc": "PLC Client",
    "processing": "Pull Processes",
    "process": "Pull Processes",
    "video": "Video Processes",
}

def _is_running(details)->bool:
    return isinstance(details, dict) and str(details.get("Status", "")).strip().lower() == "running"


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
        **({"destination": remote_destination} if remote_destination else {})     # line 153 - the crash
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


async def async_check_service_status(anylog_conn:AnyLogRest, service_name:str|None=None,
                                     remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE)->bool|dict|str|None:
    """
    Check whether a service is running, based on `get processes`
    :args:
        anylog_conn:AnyLogRest - connection to node
        service_name:str - service name or alias (case-insensitive); if not set, check all services
            names: TCP, REST, MCP, Operator, Blockchain Sync, Scheduler, Blobs Archiver, MQTT, MSG Client Pool,
                   MSG Broker, SMTP, Streamer, UNS Streamer, Query Pool, Kafka Consumer, gRPC, PLC Client,
                   Pull Processes, Video Processes, Publisher, Distributor, Consumer
            aliases: see SERVICE_ALIASES (ex. kafka -> Kafka Consumer)
        remote_destination:str - run request against a remote node, if so provide IP and port
        exec_mode:ExecMode - Execution mode
    :return:
        bool - service_name set: True if the service is running
        dict - service_name not set: {service: is_running} for every service
        str - COMMAND mode (AnyLog command, nothing is sent)
        None - INFO / HELP mode, or failure when exceptions are disabled
    :raise:
        ValueError - unknown service name (when FORCE_EXCEPTION is on)
        TypeError - `get processes` didn't return JSON (when FORCE_EXCEPTION is on)
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_check_service_status)
        return None

    services = await async_get_processes(anylog_conn=anylog_conn, json_format=True,
                                         remote_destination=remote_destination, exec_mode=exec_mode)
    if exec_mode != ExecMode.EXECUTE or not service_name:
        return services  # COMMAND -> command string, HELP -> None
    if not isinstance(services, dict):
        return await async_exec_logging(message=f"Unexpected `get processes` response ({type(services).__name__}) "
                                                f"- expected JSON, service status unknown",
                                        level=LevelMode.ERROR, exception_type=TypeError)

    if not service_name:
        return {name: _is_running(details) for name, details in services.items()}

    lookup = {name.lower(): name for name in services}
    key = service_name.strip().lower()
    name = lookup.get(SERVICE_ALIASES.get(key, key).lower())
    if not name:
        return await async_exec_logging(message=f"Unknown service {service_name!r} - supported: {list(services)} "
                                                f"(aliases: {list(SERVICE_ALIASES)})",
                                        level=LevelMode.ERROR, exception_type=ValueError)

    return _is_running(services[name])


def check_service_status(anylog_conn:AnyLogRest, service_name:str|None=None, remote_destination:str|None=None,
                         exec_mode:ExecMode=ExecMode.EXECUTE)->bool|dict|str|None:
    """Sync wrapper around `async_check_service_status` - see that function for the actual logic"""
    return asyncio.run(async_check_service_status(anylog_conn=anylog_conn, service_name=service_name,
                                                  remote_destination=remote_destination, exec_mode=exec_mode))


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
