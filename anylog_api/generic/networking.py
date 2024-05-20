"""
Module for network configuration of a node.
If IP / port for REST connection changes, then the consequent command(s) will fail without a change to the IP/Port values
"""

import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.__support__ import add_conditions

def __generate_connection_command(conn_type:str, internal_ip:str, internal_port:int, external_ip:str=None,
                                  external_port:int=None, bind:bool=False, threads:int=3, rest_timeout:int=30)->str:
    """
    Generate connection to network command
    :args:
        conn_type:str - connection type (TCP, REST, broker)
        internal_ip:str - internal/local  ip
        internal_port  - internal/local ip
        external_ip:str - external ip
        external_port:str - external port
        bind:bool - whether to bind or not
        threads:int - number of threads
        rest_timeout:bool - REST timeout
    :params:
        command:str - generatedd command
    :return:
        command
    """
    if conn_type.upper() == 'TCP':
        command = 'run tcp server where'
    elif conn_type.upper() == 'REST':
        command = 'run rest server where '
    elif conn_type.lower() == 'broker':
        command = 'run message broker where '

    if external_ip is not None:
        command += f'external_ip={external_ip} and '
    else:
        command += f'external_ip={internal_ip} and '
    if external_port is not None:
        command += f'external_ip={external_port} and '
    else:
        command += f'external_ip={internal_port} and '
    command += f'internal_ip={internal_ip} and internal_port={internal_port} and '

    if bind is True:
        command += ' bind=true and '
    else:
        command += ' bind=false and '
    command += f'threads={threads}'

    if conn_type.upper() == 'REST':
        command += f' timeout={rest_timeout}'

    return command


def network_connect(conn:anylog_connector.AnyLogConnector, conn_type:str, internal_ip:str, internal_port:int,
                    external_ip:str=None, external_port:int=None, bind:bool=True, threads:int=3, rest_timeout:int=30,
                    destination:str=None, view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Connect to a network
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog
        conn_type:str - connection type (TCP, REST, broker)
        internal_ip:str - internal/local  ip
        internal_port  - internal/local ip
        external_ip:str - external ip
        external_port:str - external port
        bind:bool - whether to bind or not
        threads:int - number of threads
        rest_timeout:bool - REST timeout
        view_help:bool - whether to print help information
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
    :return:
        True - Success
        False - Fails
        None - print help information
    """
    status = None
    headers = {
        'command': None,
        'User-Agent': 'AnyLog/1.23'
    }

    if conn_type.upper() not in ['TCP', 'REST'] and conn.lower() == 'broker':
        if exception is True:
            print(f"Invalid connection type {conn_type}")
        return False


    if conn_type.upper() == 'TCP':
        headers['command'] = 'run tcp server'
    elif conn_type.upper() == 'REST':
        headers['command'] = 'run rest server '
    elif conn_type.lower() == 'broker':
        headers['command'] = 'run message broker '

    add_conditions(headers, external_ip=external_ip, internal_ip=internal_ip, external_port=external_port,
                   internal_port=internal_port, bind=bind, timeout=rest_timeout, threads=threads)

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def get_network_info(conn:anylog_connector.AnyLogConnector, json_format:bool=True, destination:str=None,
                     view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Get network information
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        connections:dict - dict of AnyLog processes
        headers:dict - REST headers
    :return:
        connections
    """
    connections = {}
    headers = {
        'command': 'get connections',
        'User-Agent': 'AnyLog/1.23'
    }

    if json_format is True:
        headers['command'] += ' where format=json'
    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        connections = headers['command']
    else:
        connections = extract_get_results(conn=conn, headers=headers, exception=exception)

    return connections


def get_rest_calls(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                   return_cmd:bool=False, exception:bool=False):
    """
    stats regarding rest calls
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        rest_calls - REST call information
        headers:dict - REST headers
    :return:
        rest_calls
    """
    rest_calls = None
    headers = {
        'command': 'get rest calls',
        'User-Agent': 'AnyLog/1.23'
    }

    if destination is not None:
        headers["destination"] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        rest_calls = headers['command']
    else:
        rest_calls = extract_get_results(conn=conn, headers=headers, exception=exception)

    return rest_calls

