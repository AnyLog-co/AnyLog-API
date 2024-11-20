"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import warnings
import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.anylog_connector_support import extract_get_results


def blobs_archiver(conn:anylog_connector.AnyLogConnector, blobs_dbms:str='false', blobs_folder:str='true',
                   compress:str='true', reuse_blobs:str='true', destination:str=None, view_help:bool=False,
                   return_cmd:bool=False, exception:bool=False):
    """

    """
    headers = {
        "command": f"run blobs archiver where dbms={blobs_dbms} and folder={blobs_folder} and compress={compress} and reuse_blobs={reuse_blobs}",
        "User-Agent": "AnyLog/1.32"
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


def set_streamer(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False, return_cmd:bool=False,
                 exception:bool=False):
    headers = {
        "command": "run streamer",
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


def buffer_threshold(conn:anylog_connector.AnyLogConnector, db_name:str=None, table_name:str=None,
                     th_time:str='60 seconds', th_volume:str='10KB', write_immediate:str='false', destination:str=None,
                     view_help:bool=False, return_cmd:bool=False, exception:bool=False):

    headers = {
        "command": f"set buffer threshold where time={th_time} and volume={th_volume} and write={write_immediate}",
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
        output = headers['command']
    else:
        output = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return output


def clean_archive_files(conn:anylog_connector.AnyLogConnector, archive_delete:int=30, destination:str=None,
                        view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    headers={
        "command": f"delete archive where days = {archive_delete}",
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


def data_distributor(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                     return_cmd:bool=False, exception:bool=False):
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


def data_consumer(conn:anylog_connector.AnyLogConnector, start_data:str, destination:str=None, view_help:bool=False,
                     return_cmd:bool=False, exception:bool=False):
    headers = {
        "command": f"run data consumer where start_date={start_data}",
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
                 view_help:bool=False, return_cmd:bool=False, exception:bool=False):
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
    output = None
    headers = {
        'command': f"run operator where",
        'User-Agent': 'AnyLog/1.23'
    }

    if isinstance(create_table, bool) or str(create_table).lower() in ['true', 'false']:
        headers['command'] += f" create_table={str(create_table).lower()} and"
    else:
        if exception is True:
            warnings.warn('Invalid value for create table. Using `true` as default value')
        headers['command'] += f" create_table=true and"

    if isinstance(update_tsd_info, bool) or str(update_tsd_info).lower() in ['true', 'false']:
        headers['command'] += f" update_tsd_info={str(update_tsd_info).lower()} and"
    else:
        if exception is True:
            warnings.warn('Invalid value for update_tsd_info table. Using `true` as default value')
        headers['command'] += f" update_tsd_info=true and"
    if isinstance(compress_json, bool) or str(compress_json).lower() in ['true', 'false']:
        headers['command'] += f" compress_json={str(compress_json).lower()} and"
    else:
        if exception is True:
            warnings.warn('Invalid value for compress_json table. Using `true` as default value')
        headers['command'] += f" compress_json=true and"
    if isinstance(compress_sql, bool) or str(compress_sql).lower() in ['true', 'false']:
        headers['command'] += f" compress_sql={str(compress_sql).lower()} and"
    else:
        if exception is True:
            warnings.warn('Invalid value for compress_sql table. Using `true` as default value')
        headers['command'] += f" compress_sql=true and"
    if isinstance(archive_json, bool) or str(archive_json).lower() in ['true', 'false']:
        headers['command'] += f" archive_json={str(archive_json).lower()} and"
    else:
        if exception is True:
            warnings.warn('Invalid value for archive_json table. Using `true` as default value')
        headers['command'] += f" archive_json=true and"
    if isinstance(archive_sql, bool) or str(archive_sql).lower() in ['true', 'false']:
        headers['command'] += f" archive_sql={str(archive_sql).lower()} and"
    else:
        if exception is True:
            warnings.warn('Invalid value for archive_sql table. Using `true` as default value')
        headers['command'] += f" archive_sql=true and"
    if ledger_conn:
        headers['command'] += f" master_node={ledger_conn} and"
    if operator_id:
        headers['command'] += f" policy={operator_id} and"
    else:
        if exception is True:
            raise ValueError('Missing operator ID, cannot start `run operator` service...')

    if isinstance(threads, int):
        headers['command'] += f" threads={threads} and"
    elif threads:
        try:
            headers['command'] += f" threads={int(threads)} and"
        except Exception as error:
            if exception is True:
                raise ValueError(f'Invalid data type for threads (type: {type(threads)} | Error: {error})')
            headers['command'] += f" threads=3 and"
    else:
        if exception is True:
            warnings.warn(f'Invalid data type for threads (type: {type(threads)} | Error: {error})')
        headers['command'] += f" threads=3 and"


    if headers['command'].rsplit(' ', 1)[-1] == 'and':
        headers['command'] = headers['command'].rsplit(' ', 'and')[0]

    if destination:
        headers['destination'] = destination
    if view_help is True:
        headers['command'] = headers['command'].split('<')[-1].split('>')[0].replace("\n","").replace("\t", " ")
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = None execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return output


def run_publisher(conn:anylog_connector.AnyLogConnector, compress_json:bool=True, compress_sql:bool=True,
                  ledger_conn='!ledger_conn', dbms_file_location:str='file_name[0]', table_file_location='file_name[1]',
                  destination:str=None, view_help:bool=False, return_cmd:bool=False, exception:bool=False):
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
    status = None
    headers = {
        'command': f"run publisher",
        'User-Agent': 'AnyLog/1.23'
    }

    if isinstance(compress_json, bool) or str(compress_json).lower() in ['true', 'false']:
        headers['command'] += f" compress_json={str(compress_json).lower()} and"
    else:
        if exception is True:
            warnings.warn('Invalid value for compress JSON . Using `true` as default value')
        headers['command'] += f" compress_json=true and"
    if isinstance(compress_sql, bool) or str(compress_sql).lower() in ['true', 'false']:
        headers['command'] += f" compress_sql={str(compress_sql).lower()} and"
    else:
        if exception is True:
            warnings.warn('Invalid value for compress SQL . Using `true` as default value')
        headers['command'] += f" compress_sql=true and"
    if ledger_conn:
        headers['command'] += f" master_node={str(ledger_conn).lower()} and"
    if dbms_file_location:
        headers['command'] += f" dbms_name={str(dbms_file_location).lower()} and"
    if table_file_location:
        headers['command'] += f" table_name={str(table_file_location).lower()} and"
    if headers['command'].rsplit(' ', 1)[-1] == 'and':
        headers['command'] = headers['command'].rsplit(' ', 1)[0]

    if destination:
        headers['destination'] = destination

    if view_help is True:
        headers['command'] = headers['command'].split('<')[-1].split('>')[0].replace("\n", "").replace("\t", " ")
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
        headers['command'] = headers['command'].split('<')[-1].split('>')[0].replace("\n", "").replace("\t", " ")
        status = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return status

def get_operator(conn:anylog_connector.AnyLogConnector, json_format:bool=False, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False):
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
        if view_help == True - None
        results for query
    """
    output = None
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
                 return_cmd:bool=False, exception:bool=False):
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
        if view_help == True - None
        results for query
    """
    output = None
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
                  return_cmd:bool=False, exception:bool=False):
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
        if view_help == True - None
        if execution succeeds - True
        if execution fails - False
    """
    status = None
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
                   return_cmd:bool=False, exception:bool=False):
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
        if view_help == True - None
        if execution succeeds - True
        if execution fails - False
    """
    status = None
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

