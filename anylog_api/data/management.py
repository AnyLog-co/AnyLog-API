"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import warnings
from typing import Union
import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.__support__ import check_interval

def blobs_archiver(conn:anylog_connector.AnyLogConnector, blobs_dbms:bool=False, blobs_folder:bool=True,
                   compress:str=True, reuse_blobs:str=True, destination:str=None, view_help:bool=False,
                   return_cmd:bool=False, exception:bool=False)->Union[bool, str]:
    """
    Archive large objects such as files and images
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog
        blobs_dbms:bool - store blobs in database (requires nosql database to configured)
        blobs_folder:bool - store blobs in file
        compress:bool - compress blobs that are stored in file
        reuse_blobs:bool - avoid storing of identical images multiple times
        destination;str - Remote destination command
        return_cmd:bool - return command
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status
        headers:dict - REST headers
    :return:
        if return_cmd is True -> return command generated
        else ->
            True - success
            False - fails
    """
    headers = {
        "command": f"run blobs archiver where dbms={str(blobs_dbms).lower()} and folder={str(blobs_folder).lower()} and compress={str(compress).lower()} and reuse_blobs={str(reuse_blobs).lower()}",
        "User-Agent": "AnyLog/1.32"
    }
    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return status


def enable_streamer(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                    return_cmd:bool=False, exception:bool=False)->Union[bool, str]:
    """
    Writes streaming data to files
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog
        destination;str - Remote destination command
        return_cmd:bool - return command
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status
        headers:dict - REST headers
    :return:
        if return_cmd is True -> return command generated
        else ->
            True - success
            False - fails
    """
    headers = {
        "command": "run streamer",
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return status


def buffer_threshold(conn:anylog_connector.AnyLogConnector, db_name:str=None, table_name:str=None,
                     th_time:str='60 seconds', th_volume:str='10KB', write_immediate:bool=False, destination:str=None,
                     view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[bool, str]:
    """
    Configure time and volume thresholds for buffered streaming data
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog
        db_name:str / table_name:str - specific database / table to set a threshold against
        th_time:str - threshold time
        th_volume:str - threshold size
        write_immediate:bool - local database is immediate (independent of the calls to flush)
        destination;str - Remote destination command
        return_cmd:bool - return command
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status
        headers:dict - REST headers
    :return:
        if return_cmd is True -> return command generated
        else ->
            True - success
            False - fails
    """
    if not check_interval(time_interval=th_time, exception=exception):
        th_time = '60 seconds'

    headers = {
        "command": f"set buffer threshold where time={th_time} and volume={th_volume} and write={str(write_immediate).lower()}",
        "User-Agent": "AnyLog/1.23",
    }

    if db_name:
        headers['command'] += f" and dbms={db_name}"
        if table_name:
            headers['command'] += f" and table={table_name}"

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return status


def clean_archive_files(conn:anylog_connector.AnyLogConnector, archive_delete:int=30, destination:str=None,
                        view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[bool, str]:
    """
    Delete the files in the archive directory which are older than the specified number of days. Always have a proper
    backup prior to deleting archived data.
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog
        archive_delete:int - Number  of days to keep
        destination;str - Remote destination command
        return_cmd:bool - return command
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status
        headers:dict - REST headers
    :return:
        if return_cmd is True -> return command generated
        else ->
            True - success
            False - fails
    """
    headers={
        "command": f"delete archive where days = {archive_delete}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return status


def data_distributor(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                     return_cmd:bool=False, exception:bool=False)->Union[bool, str]:
    """
    For HA - Transfer data files to members of the cluster
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog
        destination;str - Remote destination command
        return_cmd:bool - return command
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status
        headers:dict - REST headers
    :return:
        if return_cmd is True -> return command generated
        else ->
            True - success
            False - fails
    """
    headers = {
        "command": "run data distributor",
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return output


def data_consumer(conn:anylog_connector.AnyLogConnector, start_data:int, destination:str=None, view_help:bool=False,
                     return_cmd:bool=False, exception:bool=False)->Union[bool, str]:
    """
    For HA - Pull the source file from the Operators of the cluster such that the cluster data set on this node is complete
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog
        start_data:str - Number of days back to pull data from
        destination;str - Remote destination command
        return_cmd:bool - return command
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status
        headers:dict - REST headers
    :return:
        if return_cmd is True -> return command generated
        else ->
            True - success
            False - fails
    """
    headers = {
        "command": f"run data consumer where start_date=-{int(start_data)}d",
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return output


def run_operator(conn:anylog_connector.AnyLogConnector, operator_id:str, create_table:bool=True,
                 update_tsd_info:bool=True, archive_json:bool=True, compress_json:bool=True, archive_sql:bool=False,
                 compress_sql:bool=True, ledger_conn='!ledger_conn', threads:int=3, destination:str=None,
                 view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[bool, str]:
    """
    Enable operator process
    :args:
        conn:AnyLogConnector - connection to AnyLog
        operator_id:str - (policy) ID of the operator policy
        create_table:bool - A True value creates a table if the table doesn't exist.
        update_tsd_info - True/False to update a summary table (tsd_info table in almgm dbms) with status of files ingested.
        compress_json - True/False to enable/disable compression of the JSON file.
        compress_sql - True/False to enable/disable compression of the SQL file.
        archive_json:bool - True/False to move JSON files to archive.
        archive_sql:bool - True/False to move SQL files to archive.
        threads:int - number of operator threads
        ledger_conn - The IP and Port of a Master Node (if a master node is used)
        destination;str - Remote destination command
        return_cmd:bool - return command
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
    :return:
        if return_cmd is True --> headers
        True -->  data sent
        False --> Fails to send data
    """
    headers = {
        'command': f"",
        'User-Agent': 'AnyLog/1.23'
    }
    command = f"run operator where"
    command += f" create_table={str(create_table).lower()} and" if create_table else " create_table=true and"
    command += f" update_tsd_info={str(update_tsd_info).lower()} and" if update_tsd_info else " update_tsd_info=true and"
    command += f" compress_json={str(compress_json).lower()} and" if compress_json else " compress_json=true and"
    command += f" archive_json={str(archive_json).lower()} and" if archive_json else " archive_json=true and"
    command += f" compress_sql={str(compress_sql).lower()} and" if compress_sql else " compress_sql=true and"
    command += f" archive_sql={str(archive_sql).lower()} and" if archive_sql else " archive_sql=true and"

    error = "Missing 1 or more params that are required to declare operator node"
    if ledger_conn:
        command += f" master_node={ledger_conn.lower()} and"
    else:
        error += " \n- missing ledger_conn information"
    if operator_id:
        command += f" policy={operator_id} and"
    else:
        error += "\n- missing operator_id"
    try:
        command += f" threads={int(threads)} and" if threads else " threads=3 and"
    except ValueError as error:
        command += " threads=3"
        if exception is True:
            warnings.warn(f'Invalid value for threads ({threads}), setting thread count to default 3 (Error: {error})')

    if command.rsplit(' ', 1)[-1] == 'and':
        headers['command'] = command.rsplit(' ', 1)[0]

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
        if exception is True and error != "Missing 1 or more params that are required to declare operator node":
            warnings.warn(error)
    else:
        if exception is True and error != "Missing 1 or more params that are required to declare operator node":
            raise ValueError(error)
        output = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return output


def run_publisher(conn:anylog_connector.AnyLogConnector, compress_json:bool=True, compress_sql:bool=True,
                  ledger_conn='!ledger_conn', dbms_file_location:str='file_name[0]', table_file_location='file_name[1]',
                  destination:str=None, view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[bool, str]:
    """
    Enable publisher process
    :args:
        conn:AnyLogConnector - connection to AnyLog
        compress_json:bool - True/False to enable/disable compression of the JSON file.
        compress_sql:bool - True/False to enable/disable compression of the SQL file.
        ledger_conn - The IP and Port of a Master Node (if a master node is used)
        dbms_file_location:str - where to set db name in file path
        table_file_location:str - where to set table name in file path
        destination;str - Remote destination command
        return_cmd:bool - return command
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
    :return:
        if return_cmd is True --> headers
        True -->  data sent
        False --> Fails to send data
    """
    headers = {
        'command': f"",
        'User-Agent': 'AnyLog/1.23'
    }
    command = "run publisher where"
    command += f" compress_json={str(compress_json).lower()} and" if compress_json else " compress_json=true and"
    command += f" compress_sql={str(compress_sql).lower()} and" if compress_sql else " compress_sql=true and"
    error = "Missing 1 or more params that are required to declare operator node"
    if ledger_conn:
        command += f" master_node={ledger_conn.lower()} and"
    else:
        error += "\n- missing ledger_conn information"
    command += f" dbms_file_location={dbms_file_location} and" if dbms_file_location else f" dbms_file_location=file_name[0] and"
    command += f" table_file_location={table_file_location} and" if table_file_location else " table_file_location=file_name[1] and"

    if command.rsplit(' ', 1)[-1] == 'and':
        headers['command'] = command.rsplit(' ', 1)[0]

    if destination:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return status


def get_operator(conn:anylog_connector.AnyLogConnector, json_format:bool=False, destination:str=None,
                 view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[str, dict]:
    """
    get operator
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
        else results for query
    """
    headers = {
        "command": "get operator",
        "User-Agent": "AnyLog/1.23"
    }
    if json_format is True:
        headers['command'] += " where format=json"
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers,  exception=exception)

    return output


def get_publisher(conn:anylog_connector.AnyLogConnector, json_format:bool=False, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False)->Union[str, dict]:
    """
    get publisher
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
        results for publisher
    """
    headers = {
        "command": "get publisher",
        "User-Agent": "AnyLog/1.23"
    }
    if json_format is True:
        headers['command'] += " where format=json"
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers,  exception=exception)

    return output


def exit_operator(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                  return_cmd:bool=False, exception:bool=False)->Union[str, bool]:
    """
    disconnect operator
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status:bool
        headers:dict - REST headers
    :return:
        if return_cmd == True -- command to execute
        if execution succeeds - True
        if execution fails - False
    """
    headers = {
        "command": "exit operator",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def exit_publisher(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                   return_cmd:bool=False, exception:bool=False)->Union[str, dict]:
    """
    disconnect publisher
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status:bool
        headers:dict - REST headers
    :return:
        if return_cmd == True -- command to execute
        if execution succeeds - True
        if execution fails - False
    """
    headers = {
        "command": "exit publisher",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status

