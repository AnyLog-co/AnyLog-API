import anylog_api.anylog_connector as anylog_connector
from anylog_api.__support__ import add_conditions
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.generic.get import get_help


def create_table(conn:anylog_connector.AnyLogConnector, db_name:str, table_name:str, destination:str=None,
                 view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    create table within a given database - as long as the `CREATE TABLE` statement exists in the blockchain
    :args:
        conn:AnyLogConnector - AnyLog REST connection information
        db_name:str - logical database to check if exists
        view_help:bool - whether to print information regarding function
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True if table was created, False if fails
    """
    status = None
    headers = {
        'command': f'create table {table_name} where dbms={db_name}',
        'User-Agent': 'AnyLog/1.23'
    }

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def get_tables(conn:anylog_connector.AnyLogConnector, db_name:str='*', json_format:bool=True, destination:str=None,
               return_cmd:bool=False, view_help:bool=False, exception:bool=False):
    """
    View list of tables in database (if set)
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/sql%20setup.md#the-get-tables-command
    :args:
        conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database to get tables for (if not set, then get all tables)
        json_format:bool - whether to get results in JSON dictionary
        view_help:bool - whether to view help for command
        exception:bool - whether to print error messages
    :params:
        output:str - results from REST request
        headers:dict - REST header requests
        r:request.get, error:str - REST request results
    :return:
        if success returns content (output), else None
    """
    output = None
    headers = {
        'command': f'get tables',
        'User-Agent': 'AnyLog/1.23'
    }

    if json_format is True:
        add_conditions(headers, dbms=db_name, format="json")
    else:
        add_conditions(headers, dbms=db_name)

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers,  exception=exception)

    return output


def check_table_exists(conn:anylog_connector.AnyLogConnctor, db_name:str, table_name:str, destination:str=None,
                       is_local:bool=False, return_cmd:bool=False, view_help:bool=False, exception:bool=False):
    """
    check if database exists
    :args:
        conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database to view
        table_name:str - table to check if exists
        is_local:bool - whether the table is locally exists
        destination:str - remote destination to query
        view_help:bool - whether to print help info for AnyLog command
        exception:bool - whether to print error messages
    :params:
        status:bool
        output:str - content from `get databases` request
    :return:
        exists True
        else False
    """
    status = False
    output = get_tables(conn=conn, db_name=db_name, json_format=True, destination=destination,
                        return_cmd=return_cmd, view_help=view_help, exception=exception)

    if return_cmd is True:
        status = output
    elif isinstance(output, dict) and db_name in output and table_name in output[db_name]:
        status = True
        if is_local is True:
            if output[db_name][table_name]['local'] in ['False', 'false', False]:
                status = False

    return status


def drop_table(conn:anylog_connector.AnyLogConnctor, db_name:str, table_name:str, destination:str=None,
               return_cmd:bool=False, view_help:bool=False, exception:bool=False):
    """
    Drop table from database
    :args: 
        conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database to view
        table_name:str - table to check if exists
        destination:str - remote destination to query
        view_help:bool - whether to print help info for AnyLog command
        exception:bool - whether to print error messages
    :params:
        status:bool
        output:str - content from `get databases` request
    :return:
        None - help
        command
        True - success
        False - Fails
    """
    status = None
    headers = {
        "command": f"drop table {table_name} where dbms={db_name}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def drop_table_partition(conn:anylog_connector.AnyLogConnctor, db_name:str, table_name:str, partition_table:str=None,
                         partition_keep:int=0, destination:str=None, return_cmd:bool=False, view_help:bool=False,
                         exception:bool=False):
    """
    Drop partition for a specific table from database
    :args:
        conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database to view
        table_name:str - table to check if exists
        partition_table:str - specific partition table to drop
        partition_keep:int - number of partitions to keep (default: 0)
        destination:str - remote destination to query
        view_help:bool - whether to print help info for AnyLog command
        exception:bool - whether to print error messages
    :params:
        status:bool
        output:str - content from `get databases` request
    :return:
        None - help
        command
        True - success
        False - Fails
    """
    status = None
    headers = {
        "command": f"drop partition where dbms={db_name} and table={table_name}",
        "User-Agent": "AnyLog/1.23"
    }

    if partition_table:
        headers['command'] = headers['command'].replace("drop partition", f"drop partition {partition_table}")
    elif partition_keep > 0:
        headers['command'] += f" and keep={partition_keep}"

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def get_virtual_tables(conn:anylog_connector.AnyLogConnctor, table_name:str=None, show_info:bool=False,
                       destination:str=None, return_cmd:bool=False, view_help:bool=False, exception:bool=False):
    """
    list of tables managed by the network
    :args:
        conn:AnyLogConnector - connection to AnyLog
        table_name:str - information for a specific table
        show_info:bool - whether to get results in JSON dictionary
        destination:str - remote connection to request against
        view_help:bool - whether to view help for command
        exception:bool - whether to print error messages
    :params:
        output:str - results from REST request
        headers:dict - REST header requests
    :return:
        output
    """
    output = None
    headers = {
        "command": "get virtual tables",
        "User-Agent": "AnyLog/1.23"
    }

    if show_info is True:
        headers['command'] += " info"
    if table_name is not None:
        headers['command'] += f" where table={table_name}"

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers,  exception=exception)

    return output

