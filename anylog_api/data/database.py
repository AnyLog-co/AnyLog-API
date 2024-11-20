"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.anylog_connector_support import extract_get_results


def check_database(conn:anylog_connector.AnyLogConnector, db_name:str, json_format:bool=True, destination:str=None,
                   view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Check whether a database exists
    :cmd:
        get databases where format=json
    :args:
        conn:anylog_connector.AnyLogConnector - Connection to AnyLog
        db_name:str - logical database name
        json_format:bool - return results in JSON format
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        ret_value:bool - Value returned
        headers:dict - REST headers
    :return:
        ret_value
    """
    ret_value = False
    headers = {
        'command': "get databases",
        'User-Agent': 'AnyLog/1.23'
    }

    if json_format is True:
        headers['command'] += " where format=json"
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        ret_value = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)
        if isinstance(output, dict):
            ret_value = db_name in output

    return ret_value


def check_table(conn:anylog_connector.AnyLogConnector, db_name:str, table_name:str, json_format:bool=True,
                destination:str=None, view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Check whether a table exists in a given database
    :cmd:
        get databases where database={db_name} and format=json
    :args:
        conn:anylog_connector.AnyLogConnector - Connection to AnyLog
        db_name:str - logical database name
        table_name:str - table name
        json_format:bool - return results in JSON format
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        ret_value:bool - Value returned
        headers:dict - REST headers
    :return:
        ret_value
    """
    ret_value = False
    headers = {
        'command': f"get tables where dbms={db_name}",
        'User-Agent': 'AnyLog/1.23'
    }

    if json_format is True:
        headers['command'] += " where format=json"
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        ret_value = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)
        if isinstance(output, dict):
            ret_value = table_name in output[db_name]

    return ret_value


def connect_dbms(conn:anylog_connector.AnyLogConnector, db_name:str, db_type:str='sqlite', db_ip:str=None,
                 db_port:int=None, db_user:str=None, db_password:str=None, memory:bool=False, destination:str=None,
                 view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Connect to database
    :command:
        connect dbms {db_name} where type={db_type} and ..
    :args:
        conn:anylog_connector.AnyLogConnector - Connection to AnyLog
        db_name:str - logical database name
        db_type:str - physical database name
        db_ip:str - for non-SQLite the IP address
        db_port:int - for non-SQLite - port associated with database
        db_user:str - username for database
        db_password:str - password associated with user
        destination:str - remote connection information
        view_help:bool - print help information
        return_cmd:bool - return command to be executed
        exception:bool - print exception
    :params:
        output:str - command if return_cmd is True
        headers:dict - REST header information
    :return:
        output
    """
    output = None
    headers = {
        "command": f"connect dbms {db_name} where type={db_type}",
        "User-Agent": "AnyLog/1.23"
    }
    if check_database(conn=conn, db_name=db_name, json_format=True, destination=destination, view_help=view_help,
                      return_cmd=return_cmd, exception=exception) is True:
        if return_cmd is True:
            output = headers['command']
        return output

    if db_ip:
        headers['command'] += f" and ip={db_ip}"
    if db_port:
        headers['command'] += f" and port={db_port}"
    if db_user:
        headers['command'] += f" and user={db_user}"
    if db_password:
        headers['command'] += f" and password={db_password}"
    if db_type == 'sqlite' and memory == 'true':
        headers['command'] += " and memory=true"

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return output


def create_table(conn:anylog_connector.AnyLogConnector, db_name:str, table_name:str, destination:str=None,
                 view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Create pre-defined table
        - blockchain.ledger
        - almgm.tsd_info
        - any table definition on the blockchain
    :args:
        conn:anylog_connector.AnyLogConnector - Connection to AnyLog
        db_name:str - logical database name
        table_name:str - table name
        json_format:bool - return results in JSON format
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        output:str - command if return_cmd is True
        headers:dict - REST header information
    :return:
        output
    """
    output = None
    headers = {
        "command": f"create table {table_name} where dbms={db_name}",
        "User-Agent": "AnyLog/1.23"
    }

    if check_table(conn=conn, db_name=db_name, table_name=table_name, destination=destination, view_help=view_help,
                   return_cmd=return_cmd, exception=exception) is True:
        if return_cmd is True:
            output = headers['command']
        return output

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return output



def set_data_partition(conn:anylog_connector.AnyLogConnector, db_name:str, table_name:str='*',
                       partition_column:str='insert_timestamp', partition_interval:str='14 days', destination:str=None,
                       view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    output = None
    headers = {
        "command": f"partition {db_name} {table_name} using {partition_column} by {partition_interval}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return output


def drop_data_partition(conn:anylog_connector.AnyLogConnector, db_name:str, table_name:str='*', partition_keep:int=3,
                        destination:str=None, view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    output = None
    headers = {
        "command": f"drop partition where dbms={db_name} and table={table_name} and keep={partition_keep}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return output




