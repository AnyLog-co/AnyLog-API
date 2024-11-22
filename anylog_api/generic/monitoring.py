"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import warnings
from typing import Union

import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import extract_get_results


def get_node_stats(conn:anylog_connector.AnyLogConnector, service:str="operator", topic:str="summary",
                   json_format:bool=True, destination:str=None, view_help:bool=False, return_cmd:bool=False,
                   exception:bool=False)->Union[bool,str,None]:
    """
    Provide statistics on a service enabled omn the node
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog/EdgeLAke
        service:str - Node type to get information for
            * operator
            * publisher
        topic:str - type of information to get
            * summary
            * files
            * inserts
        json_format:bool - Return results in JSON format
        destination:str - remote connection to execute against
        view_help:bool - print information about command
        return_cmd:bool - return generated command
        exception:bool - raise exceptions if occur
    :params:
        output = None
        headers:dict - REST header information
    :return:
        if return_cmd is True - return command
        else - return generated results for request
    """
    output = None
    if service not in ['publisher', 'operator']:
        if exception is True:
            warnings.warn(ValueError(f'Invalid value type {service} for service options. Using default `operator` instead. Supported Services: operator or publisher'))
        service = 'operator'
    if topic not in ['summary', 'inserts', 'files']:
        if exception is True:
            warnings.warn(ValueError(f'Invalid value type {topic} for topic options. Using default `summary` instead. Supported Topics: summary, files or inserts'))
        topic = 'summary'

    headers = {
        "command": f"get stats where service={service} and topic={topic}",
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
    """
    Get information on the status of the disk addressed by the path.
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog/EdgeLAke
        params:str - type of information regarding disk space
            * usage
            * total
            * free
            * used
            * percent
        json_format:bool - Return results in JSON format
        destination:str - remote connection to execute against
        view_help:bool - print information about command
        return_cmd:bool - return generated command
        exception:bool - raise exceptions if occur
    :params:
        output = None
        headers:dict - REST header information
    :return:
        if return_cmd is True - return command
        if invalid param  thenwe return a ValueError or None depending on exception
        else - return generated results for request
    """
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
    elif param not in ["usage", "free", "total", "used", "percentage"] and exception is True:
        raise ValueError(f"Invalid param ({param}) for getting disk space information")
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def get_node_info(conn:anylog_connector.AnyLogConnector, attribute_function:str, attribute:str=None,
                  destination:str=None, view_help:bool=False, return_cmd:bool=False,
                  exception:bool=False):
    """
    Get physical machine information based on a given attribute
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog/EdgeLAke
        attribute_function:str - attribute function
            * cpu_percent
            * cpu_times
            * getloadavg
            * swap_memory
            * disk_io_counter
            * net_io_counter
        attribute:str - speicific attribute for function
            * cpu_percent
            * cpu_times - 'user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice'
            * getloadavg - 'user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice'
            * swap_memory
            * disk_io_counter - 'total', 'used', 'free', 'percent', 'sin', 'sout'
            * net_io_counter - 'bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv', 'errin', 'errout', 'dropin', 'dropout'
        destination:str - remote connection to execute against
        view_help:bool - print information about command
        return_cmd:bool - return generated command
        exception:bool - raise exceptions if occur
    :params:
        output = None
        is_invalid:bool
        options:dict - attribute_functions / attribute information
        headers:dict - REST header information
    :return:
        if return_cmd is True - return command
        if invalid param  then return a ValueError or None depending on exception
        else - return generated results for request
    """
    output = None
    is_invalid = False
    options = {
        "cpu_percent": None,
        "cpu_times": ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice'],
        "cpu_times_percent": ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest',
                              'guest_nice'],
        "getloadavg": None,
        "swap_memory": ['total', 'used', 'free', 'percent', 'sin', 'sout'],
        "disk_io_counters": ['read_count', 'write_count', 'read_bytes', 'write_bytes', 'read_time', 'write_time',
                             'read_merged_count', 'write_merged_count', 'busy_time'],
        "net_io_counters": ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv', 'errin', 'errout', 'dropin',
                            'dropout']
    }

    headers = {
        "command": "get node info",
        "User-Agent": "AnyLog/1.23"
    }

    if attribute_function not in options:
        is_invalid = True
        if exception is True:
            raise ValueError(f'Invalid value attribute function value {attribute_function}. Supported values: {",".join(list(options.keys()))}')
    elif attribute and not attribute not in options[attribute_function]:
        is_invalid = True
        if exception is True:
            raise ValueError(f'Invalid attribute {attribute} for attribute function {attribute_function}. Supported values {",".join(options[attribute_function])}')
    else:
        headers['command'] += f" {attribute_function}"
        if attribute:
            headers['command'] += f" {attribute}"

    if destination is True:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif is_invalid is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output

