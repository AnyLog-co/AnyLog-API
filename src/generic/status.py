"""
Node state - status, running services and connectivity to the rest of the network
"""
import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, build_headers, exec_info
from src.core.support_logging import LevelMode, async_exec_logging

# shorthand -> service name as returned by `get processes`
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
    """Whether a `get processes` entry has Status = Running"""
    return isinstance(details, dict) and str(details.get("Status", "")).strip().lower() == "running"


# ---------------------------------------------------------------------------------------------------------------------
# Status / processes
# ---------------------------------------------------------------------------------------------------------------------
async def async_get_status(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None,
                           exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Get the node's status
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        json_format:bool - return results in JSON format
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        get status [where format=json]
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "get status where format=json", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        node status
    :sample-output:
        {"assigned_name": "anylog-generic@172.20.0.3:32548", "status": "running", "profiling": false, "uptime": "00:05:08"}
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_status)

    headers = build_headers(command="get status where format=json" if json_format else "get status",
                            remote_destination=remote_destination)
    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def get_status(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None,
               exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_get_status` - see that function for details"""
    return asyncio.run(async_get_status(anylog_conn=anylog_conn, json_format=json_format,
                                        remote_destination=remote_destination, exec_mode=exec_mode))


async def async_get_processes(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None,
                              exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Get the node's services (processes) and their state
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        json_format:bool - return results in JSON format
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        get processes [where format=json]
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "get processes where format=json", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        table or JSON of node processes
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_processes)

    headers = build_headers(command="get processes where format=json" if json_format else "get processes",
                            remote_destination=remote_destination)
    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def get_processes(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None,
                  exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_get_processes` - see that function for details"""
    return asyncio.run(async_get_processes(anylog_conn=anylog_conn, json_format=json_format,
                                           remote_destination=remote_destination, exec_mode=exec_mode))


async def async_check_service_status(anylog_conn:AnyLogRest, service_name:str|None=None,
                                     remote_destination:str|None=None,
                                     exec_mode:ExecMode=ExecMode.EXECUTE)->bool|dict|str|None:
    r"""
    Check whether a service is running, based on `get processes`
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        service_name:str - service name or alias (case-insensitive); if not set, return all processes
            names: TCP, REST, MCP, Operator, Blockchain Sync, Scheduler, Blobs Archiver, MQTT, MSG Client Pool,
                   MSG Broker, SMTP, Streamer, UNS Streamer, Query Pool, Kafka Consumer, gRPC, PLC Client,
                   Pull Processes, Video Processes, Publisher, Distributor, Consumer
            aliases: see SERVICE_ALIASES (ex. kafka -> Kafka Consumer)
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :params:
        services:dict - `get processes` result
    :cmd:
        get processes where format=json
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "get processes where format=json", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        bool - service_name set: True if the service is running
        dict - service_name not set: `get processes` result as-is
        str - COMMAND mode (AnyLog command, nothing is sent)
        None - INFO / HELP mode, or failure when exceptions are disabled
    :raise:
        ValueError - unknown service name (when FORCE_EXCEPTION is on)
        TypeError - `get processes` didn't return JSON (when FORCE_EXCEPTION is on)
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_check_service_status)

    services = await async_get_processes(anylog_conn=anylog_conn, json_format=True,
                                         remote_destination=remote_destination, exec_mode=exec_mode)
    if exec_mode != ExecMode.EXECUTE or not service_name:
        return services     # COMMAND -> command string | HELP -> None | no service_name -> all processes
    if not isinstance(services, dict):
        return await async_exec_logging(message=f"Unexpected `get processes` response ({type(services).__name__}) "
                                                f"- expected JSON, service status unknown",
                                        level=LevelMode.ERROR, exception_type=TypeError)

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
    """Sync wrapper around `async_check_service_status` - see that function for details"""
    return asyncio.run(async_check_service_status(anylog_conn=anylog_conn, service_name=service_name,
                                                  remote_destination=remote_destination, exec_mode=exec_mode))


# ---------------------------------------------------------------------------------------------------------------------
# Connectivity
# ---------------------------------------------------------------------------------------------------------------------
async def async_test_node(anylog_conn:AnyLogRest, exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Test the connected node's TCP / REST services and its connection to the metadata
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        exec_mode:ExecMode - Execution mode
    :cmd:
        test node
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "test node", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        node test results
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_test_node)

    headers = build_headers(command="test node")
    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def test_node(anylog_conn:AnyLogRest, exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_test_node` - see that function for details"""
    return asyncio.run(async_test_node(anylog_conn=anylog_conn, exec_mode=exec_mode))


async def async_test_network(anylog_conn:AnyLogRest, exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Test the connection from the connected node to every node in the network
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        exec_mode:ExecMode - Execution mode
    :cmd:
        test network
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "test network", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        network communication status
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_test_network)

    headers = build_headers(command="test network")
    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def test_network(anylog_conn:AnyLogRest, exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_test_network` - see that function for details"""
    return asyncio.run(async_test_network(anylog_conn=anylog_conn, exec_mode=exec_mode))
