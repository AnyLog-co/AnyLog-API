"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import extract_get_results


def get_node_stats(conn:anylog_connector.AnyLogConnector, json_format:bool=True, destination:str=None,
                      view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Get base node insight
    """
    headers = {
        "command": "get stats where service = operator and topic=summary",
        "User-Agent": "AnyLog/1.23"
    }
    if json_format is True:
        headers['command'] += " and format=json"
    if destination is not None:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output

def get_disk_space(conn:anylog_connector.AnyLogConnector, param:str, path:str='.', json_format:bool=True,
                   destination:str=None, view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    if param not in ["usage","free","total","used","percentage"]:
        raise f"Invalid param ({param}) for getting disk space information"
    headers = {
        "command": f"get disk {param} {path}",
        "User-Agent": "AnyLog/1.23"
    }
    if json_format is True:
        headers['command'] += " and format=json"
    if destination is not None:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output

def get_node_info(conn:anylog_connector.AnyLogConnector, param:list=[], json_format:bool=True, destination:str=None,
                  view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    options = {
        "cpu_percent": None,
        "cpu_times": ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice'],
        "cpu_times_percent": ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice'],
        "getloadavg": None,
        "swap_memory": ['total', 'used', 'free', 'percent', 'sin', 'sout'],
        "disk_io_counters": ['read_count', 'write_count', 'read_bytes', 'write_bytes', 'read_time', 'write_time', 'read_merged_count', 'write_merged_count', 'busy_time'],
        "net_io_counters": ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv', 'errin', 'errout', 'dropin', 'dropout']
    }

    if param[0] not in list(options.keys()):
        raise f"Base param {param} not supported (Base Params: {','.join(list(options.keys()))})"
    elif options[param[0]] is not None and all(x in options[param[0]] for x in param[1:]) is False:
        raise f"Base sub param(s) {param[1:]} not supported (Supported Params: {','.join(options[param[0]])})"
    elif options[param[0]] is None and len(param) > 1:
        raise f"Param {param} does not allow for a sub parameter"

    headers = {
        "command": "get node info",
        "User-Agent": "AnyLog/1.23"
    }
    if isinstance(param, list):
        headers['command'] += f" {' '.join(param)}"
    elif isinstance(param, str):
        headers['command'] += f" {param}"
    if json_format is True:
        headers['command'] += " and format=json"
    if destination is not None:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output

