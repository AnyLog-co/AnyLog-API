"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
# URL https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#get-command
import warnings
from typing import Union

import anylog_api.anylog_connector as anylog_connector
from anylog_api.anylog_connector_support import extract_get_results


def get_help(conn:anylog_connector.AnyLogConnector, cmd:str=None, get_index:bool=False, exception:bool=False):
    """
    Get help information about command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/getting%20started.md#the-help-command
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        is_index:bool - get index information for a "topic"
        cmd:str - command to get help with
        exception:bool - whether to print exception
    :params:
        output:str - results
        headers:dict - REST headers
    :output:
        prints help information for a given command
    """
    index_options = ['api', 'background processes', 'blockchain', 'cli', 'config', 'configuration', 'data', 'dbms',
                     'debug', 'enterprise', 'file', 'help', 'high availability', 'index', 'internal', 'json', 'log', 'metadata',
                     'monitor', 'node info', 'profile', 'profiling', 'query', 'script', 'secure network', 'streaming',
                     'test suite', 'unstructured data']
    headers = {
        "command": "help",
        "User-Agent": "AnyLog/1.23",
    }

    if get_index is True and cmd in index_options:
        headers['command'] += f" index {index_options}"
    elif get_index is True and not cmd:
        headers['command'] += f" index"
    else:
        if get_index is True and cmd not in index_options and exception is True:
            warnings.warn(f'Invalid option for indexing, providing regualr help.\nSupported cmds for indexing: {",".join(index_options)}')
        headers['command'] += f" {cmd}"

    if cmd is not None:
        headers['command'] += " " + cmd

    output = extract_get_results(conn=conn, headers=headers, exception=exception)
    print(f"Inputted Command: {headers['command']} \n{output}")


def get_status(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False, return_cmd:bool=False,
               exception:bool=False)->Union[bool, None]:
    """
    Check whether node is running
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-status-command
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        json_formatL:bool - return contennt in JSON format
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status:bool - whether node is accessible
        headers:dict - REST headers
        output:str - results
    :return:
        is return_cmd is True -> the return command
        else ->
            True - node accessible
            False - node not accessible
    """
    status = None
    headers = {
        "command": "get status where format=json",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        status = False
        output = extract_get_results(conn=conn, headers=headers, exception=exception)
        if isinstance(output, dict) and 'Status' in output and ('not' not in output['Status'] and 'running' in output['Status']):
            status = True
        elif isinstance(output, str) and ('not' not in output and 'running' in output):
            status = True

    return status


def get_license_key(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False, return_cmd:bool=False,
               exception:bool=False)->Union[str, None]:
    """
    Return AnyLog license info
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-status-command
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        headers:dict - REST headers
        output:str
    :return:
        if return_cmd is True -> returns command
        else -> returns license key
    """
    headers = {
        "command": "get license",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def get_dictionary(conn:anylog_connector.AnyLogConnector, variable:str=None, json_format:bool=True, destination:str=None,
                   view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[dict, str, None]:
    """
    get dictionary
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-dictionary-command
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        variable:str - variable in dictionary to get back
        json_format:bool - return results in JSON format
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        headers:dict - REST headers
        output:str - results
    :return:
        if return_cmd is True -> return command
        else if variable is set and format is dict aad variable exists -> return variable
        else if variable is set and format is dict but variable DNE -> return None
        else -> return JSON
    """
    headers = {
        "command": "get dictionary",
        "User-Agent": "AnyLog/1.23"
    }

    if json_format is True:
        headers['command'] += " where format=json"
    if destination:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)
        if isinstance(output, dict) and variable and variable in output:
            output = output[variable]
        elif isinstance(output, dict) and variable and variable not in output:
            output = None
            if exception is True:
                warnings.warn(f"Failed to locate {variable} in AnyLog/EdgeLake dictionary")

    return output


def get_node_name(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                  return_cmd:bool=False, exception:bool=False):
    """
    get node name
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#get-node-name
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        headers:dict - REST headers
        output:str - results
    :return:
        headers
    """
    output = None
    headers = {
        "command": "get node name",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def get_hostname(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False)->Umion[str, None]:
    """
    get hostname for local machine
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        headers:dict - REST headers
        output:str - results
    :return:
        if return_cmd is True -> command
        else -> hostname
    """
    output = None
    headers = {
        "command": "get hostname",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def get_version(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                return_cmd:bool=False, exception:bool=False)->Union[str, None]:
    """
    get version for AnyLog
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        headers:dict - REST headers
        output:str - results
    :return:
        if return_cmd is True -> command
        else -> version
    """
    output = None
    headers = {
        "command": "get version",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def get_processes(conn:anylog_connector.AnyLogConnector, process:str=None, is_running:bool=False, json_format:bool=True,
                  destination:str=None, view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[str, dict, bool]:
    """
    List the background processes and their status
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        process:str - specific process to get information for
        is_running:bool - get whether process is running or not
        json_format:bool - return results in JSON format
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        headers:dict - REST headers
        output:str - results
    :return:
        if return_cmd is True -> command
        else if json_format is true ->
            if process and is_running -> return True if process is active, False if not
            else if process -> return dict about process
        else if json_format is True and process ->
            * warning
            * None
        else -> full list of processes
    """
    options = ['TCP', 'REST', 'Operator', 'Blockchain Sync', 'Scheduler', 'Blobs Archiver', 'MQTT', 'Message Broker',
               'SMTP', 'Streamer', 'Query Pool', 'Kafka Consumer', 'gRPC', 'Publisher', 'Distributor', 'Consumer']

    headers = {
        "command": "get processes",
        "User-Agent": "AnyLog/1.23"
    }

    if json_format is True:
        headers['command'] += " where format=json"
    if destination:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)
        if isinstance(output, dict) and process and process in options:
            output = output[process]
            if is_running is True and output['Status'] == 'Running':
                output = True
            elif is_running is True and output['Status'] == 'Not declared':
                output = False

    return output


def get_event_log(conn:anylog_connector.AnyLogConnector, json_format:bool=True, destination:str=None,
                  view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[str, dict]:
    """
    Get recently executed commands
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        process:str - specific process to get information for
        json_format:bool - return results in JSON format
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        headers:dict - REST headers
        output:str - results
    :returnn:
        if return_cmd is True -> return command
        else -> return results
    """
    headers = {
        "command": "get event log",
        "User-Agent": "AnyLog/1.23"
    }

    if json_format is True:
        headers['command'] += " where format=json"
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)
    return output


def get_error_log(conn:anylog_connector.AnyLogConnector, json_format:bool=True, destination:str=None,
                  view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[str, dict]:
    """
    Get recently occurred errors
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        process:str - specific process to get information for
        json_format:bool - return results in JSON format
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        headers:dict - REST headers
        output:str - results
    :returnn:
        if return_cmd is True -> return command
        else -> return results
    """
    headers = {
        "command": "get error log",
        "User-Agent": "AnyLog/1.23"
    }

    if json_format is True:
        headers['command'] += " where format=json"
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)
    return output


def get_echo_log(conn:anylog_connector.AnyLogConnector, json_format:bool=True, destination:str=None,
                  view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[str, dict]:
    """
    Get the echo commands from the current nodes and peer nodes.
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        process:str - specific process to get information for
        json_format:bool - return results in JSON format
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        headers:dict - REST headers
        output:str - results
    :returnn:
        if return_cmd is True -> return command
        else -> return results
    """
    headers = {
        "command": "get error queue",
        "User-Agent": "AnyLog/1.23"
    }

    if json_format is True:
        headers['command'] += " where format=json"
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)
    return output