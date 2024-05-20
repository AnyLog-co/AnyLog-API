import re

import anylog_api.anylog_connector as anylog_connector
from anylog_api.__support__ import add_conditions
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.generic.get import get_help


def get_streaming(conn:anylog_connector.AnyLogConnector, json_format:bool=False, destination:str=None,
                  view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    get streaming
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        json_format:bool - Set `get operator` output in JSON format
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        output - content returned
        headers:dict - REST headers
    :return:
        if return_cmd == True -- command to execute
        if view_help == True - None
        results for query
    """
    output = None
    headers = {
        "command": "get streaming",
        "User-Agent": "AnyLog/1.23"
    }

    if json_format is True:
        add_conditions(headers, format="json")

    if destination is not None:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers,  exception=exception)

    return output


def get_data_nodes(conn:anylog_connector.AnyLogConnector, company_name:str=None, db_name:str=None, table_name:str=None,
                   sort:tuple=(), destination:str=None, view_help:bool=False, return_cmd:bool=False,
                   exception:bool=False):
    """
    get data nodes
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        json_format:bool - Set `get operator` output in JSON format
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        output - content returned
        headers:dict - REST headers
    :return:
        if return_cmd == True -- command to execute
        if view_help == True - None
        results for query
    """
    output = None
    headers = {
        "command": "get data nodes",
        "User-Agent": "AnyLog/1.23"
    }

    add_conditions(headers, company=company_name, dbms=db_name, table=table_name, sort=sort)

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers,  exception=exception)

    return output


def set_buffer_threshold(conn:anylog_connector.AnyLogConnector, db_name:str=None, table_name:str=None,
                         time:str='60 seconds', volume:str='10KB', write_immediate:bool=False, destination:str=None,
                         return_cmd:bool=False, view_help:bool=False, exception:bool=False):
    """
    Setting the buffer threshold
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#setting-and-retrieving-thresholds-for-a-streaming-mode
    :args:
        anylog_conn:AnyLogConnector - conneection to AnyLog via REST
        db_name:str - logical database name
        table_name:str - table name
        time:str - The time threshold to flush the streaming data
        volume:str - The accumulated data volume that calls the data flush process
        write_immediate:bool - Local database is immediate (independent of the calls to flush)
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - view help
    """
    status = None
    headers = {
        'command': 'set buffer threshold ',
        'User-Agent': 'AnyLog/1.23'
    }
    if destination:
        headers['destination'] = destination

    add_conditions(headers, time=time, volume=volume, dbms=db_name, table=table_name, write_immediate=write_immediate)

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, headers=headers, payload=None, exception=exception)

    return status


def enable_streamer(conn:anylog_connector.AnyLogConnector, destination:str=None, return_cmd:bool=False,
                    view_help:bool=False, exception:bool=False)->bool:
    """
    run streamer
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#streamer-process
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog Node
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - print help information
    """
    status = None
    headers = {
        'command': 'run streamer',
        'User-Agent': 'AnyLog/1.23'
    }
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, headers=headers, payload=None, exception=exception)

    return status


def set_partitions(conn:anylog_connector.AnyLogConnector, db_name:str='*', table:str=None,
                   partition_ts_column:str='insert_timestamp', time_interval:str='day', destination:str=None,
                   return_cmd:bool=False, view_help:bool=False, exception:bool=False):
    """
    Partition a table or a group of tables by time interval
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#partition-command
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog
        db_name:str - logical database name (* - all)
        table:str - specific table to partition
        partition_ts_column:str - Timestamp column to partition by
        time_interval:str - interval period for each partition
            -> year
            -> month
            -> week
            -> day
        destination:str - Remote destination to send request against
        return_cmd:bool - return command
        view_help:bool - explain command
        exception:bool - print exceptions
    :params:
        status:bool
        time_interval_pattern - pattern to check against
        headers:dict - REST header information
    :return:
        None - didn't run
        command - when return_cmd is true
        True - success
        False - fails
    """
    status = None
    time_interval_pattern = r'^\d*\s*(year|years|month|months|week|weeks|day|days)$'
    if not bool(re.match(time_interval_pattern, time_interval.strip())):
        if exception is True:
            print(f"Invalid interval value {time_interval} - time interval options: year, month, week, day")
        return status

    headers = {
        "command": f"partition {db_name} using {partition_ts_column} by {time_interval.lower()}",
        "User-Agent": "AnyLog/1.23"
    }
    if table:
        headers['command'] = f"partition {db_name} {table} using {partition_ts_column} by {time_interval.lower()}"
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, headers=headers, payload=None, exception=exception)

    return status


def get_partitions(conn:anylog_connector.AnyLogConnector, db_name:str=None, table:str=None, json_format:bool=False,
                   destination:str=None, return_cmd:bool=False, view_help:bool=False,exception:bool=False):
    """
    Get partition information
    :args:
        conn:anylog_connector.AnyLogConnector - REST connection information
        db_name:str - logical database name
        table:str - specific table to get partition (tables) for
        json_format:bool - return in JSON format
        destination:str - execute command remotely
        return_cmd:bool - return generated command
        view_help:bool - print help information for command
        exception:bool - print exceptions
    :params:
        output - output to return
        headers:dict - REST headers
    :return:
        None - print help / no command executed
        command - if return_cmd is True
        results
    """
    output = None
    headers = {
        "command": "get partitions",
        "User-Agent": "AnyLog/1.23"
    }

    if json_format is True and None not in [db_name, table]:
        add_conditions(headers, dbms=db_name, table=table, format='json')
    elif None not in [db_name, table]:
        add_conditions(headers, dbms=db_name, table=table)
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def run_blobs_archiver(conn:anylog_connector.AnyLogConnector, blobs_dir:str='!blobs_dir', archive_dir:str='!archive_dir',
                       dbms_store:bool=False, store_file:bool=True, compress_file:bool=True, destination:str=None,
                       return_cmd:bool=False, view_help:bool=False,exception:bool=False):
    """
    Enable blobs archiver
    :args:
        conn:anylog_connector.AnyLogConnector - REST connection information
        blobs_dir:str - path to store blobs data in directory
        archive_dir:str - path to store archive data in directory
        dbms_store:bool - whether to store in NoSQL (MongoDB) database
        store_file:bool - store blobs in a local file
        compress_file:bool - compress stored file
        destination:str - execute command remotely
        return_cmd:bool - return generated command
        view_help:bool - print help information for command
        exception:bool - print exceptions
    :params:
        status
        headers:dict - REST header information
    """
    status = None
    headers = {
        "command": "run blobs archiver",
        "User-Agent": "AnyLog/1.23"
    }
    add_conditions(headers, blobs_dir=blobs_dir, archive_dir=archive_dir, dbms=dbms_store, file=store_file,
                   compress=compress_file)
    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, headers=headers, payload=None, exception=exception)

    return status


def get_blobs_archiver(conn:anylog_connector.AnyLogConnector, destination:str=None, return_cmd:bool=False,
                       view_help:bool=False,exception:bool=False):
    """
    Get blobs archiver
    :args:
        conn:anylog_connector.AnyLogConnector - REST connection information
        destination:str - execute command remotely
        return_cmd:bool - return generated command
        view_help:bool - print help information for command
        exception:bool - print exceptions
    :params:
        output
        headers:dict - REST header information
    """
    output = None
    headers = {
        "command": "get blobs archiver",
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output