"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import warnings
from multiprocessing.managers import Value

import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import extract_get_results


def get_node_stats(conn:anylog_connector.AnyLogConnector, service:str, topic:str, json_format:bool=True,
                      destination:str=None, view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Get base node insight
    :sample output:
    {
        'node name' : 'edgex-operator4@10.10.1.203:32148',
        'status' : 'Active',
        'operational time' : '373:16:13',
        'processing time' : '373:13:56',
        'elapsed time' : '00:00:05',
        'new rows' : 3,
        'total rows' : 67878,
        'new errors' : 0,
        'total errors' : 0,
        'avg. rows/sec' : 0.05
    }
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog
        service:str - service to get information for
            * operator
            * publisher
        topic:str - type of information to get
            * summary
            * file
            * insert
        json_format:bool - return results in JSON format
        destination:str - remote connection to send request against
        view_help:bool - print help information regarding command
        return_cmd:bool - return generated command rather than execute command
        exception:bool - raise exceptions / warnings if any
    :params:
        output
        headers:dict - REST header
    :return:
        if return_cmd is True -> generated command | else request result
    """
    output = None
    headers = {
        "command": f"get stats where",
        "User-Agent": "AnyLog/1.23"
    }
    if service not in ['publisher', 'operator']:
        warnings.warn(f"Invalid Value for `service` - using 'operator'")
        headers['command'] += ' service=operator and'
    else:
        headers['command'] += f' service={service} and'
    if topic not in ['summary', 'file', 'insert']:
        warnings.warn(f"Invalid Value for `topic` - using 'summary'")
        headers['command'] += " topic=summary and"
    else:
        headers['command'] += f" topic={topic} and"

    if json_format is True:
        headers['command'] += " format=json"
    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif return_cmd is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def get_disk_space(conn:anylog_connector.AnyLogConnector, param:str, path:str='.', json_format:bool=True,
                   destination:str=None, view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Get information on the status of the disk addressed by the path.
    :args:
        conn:anylog_connector.AnyLogConnector - AnyLog connection information
        param:str - disk space option
            * usage
            * free
            * total
            * used
            * percentage
        path:str - directory path to view disk space
        json_format:bool - return results in JSON format
        destination:str - remote destination to query against
        view_help:bool - print help for command
        return_cmd:bool - return generated command
        exception:bool - raise any exceptions and/or errors
    :params:
        output
        header:dict - REST header information
    :return:
        if return_cmd is True -> return generated command | else return result
    """
    output = None
    headers = {
        "command": f"get disk {param} {path}",
        "User-Agent": "AnyLog/1.23"
    }

    if param not in ["usage","free","total","used","percentage"]:
        raise ValueError(f"Invalid param ({param}) for getting disk space information")
    if json_format is True:
        headers['command'] += " and format=json"
    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def get_node_info(conn:anylog_connector.AnyLogConnector, param:str, attributes:list=[],
                  destination:str=None, view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    get monitored information on the current node
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        param:str - parameter to get information for
            * cpu_percent
            * cpu_times
            * cpu_times_percent
            * getloadavg
            * swap_memory
            * disk_io_counters
            * net_io_counters
        attributes:list - list of sub options for param (view options for a complete list)
        destination:str - remote destination to query against
        view_help:bool - print help for command
        return_cmd:bool - return generated command
        exception:bool - raise any exceptions and/or errors
    :params:
        output
        header:dict - REST header information
    :return:
        if return_cmd is True -> return generated command | else return result
    """
    headers = {
        "command": "get node info",
        "User-Agent": "AnyLog/1.23"
    }

    options = {
        "cpu_percent": None,
        "cpu_times": ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice'],
        "cpu_times_percent": ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice'],
        "getloadavg": None,
        "swap_memory": ['total', 'used', 'free', 'percent', 'sin', 'sout'],
        "disk_io_counters": ['read_count', 'write_count', 'read_bytes', 'write_bytes', 'read_time', 'write_time', 'read_merged_count', 'write_merged_count', 'busy_time'],
        "net_io_counters": ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv', 'errin', 'errout', 'dropin', 'dropout']
    }

    if param not in options:
        raise ValueError("Invalid value {param} to `get node info` for")
    else:
        headers['command'] += f" {param} "
    for attribute in attributes:
        if attribute in options[param]:
            headers['command'] += f"{attribute} "
        elif exception is True:
            warnings.warn(f'Invalid attribute {attribute} for param of type {param}')

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif return_cmd is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output

