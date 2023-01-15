import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'python_rest'))

from anylog_connector import AnyLogConnector
import generic_get_calls
import generic_post_calls


def declare_buffer_threshold(anylog_conn:AnyLogConnector, anylog_configs:dict, exception:bool=False):
    """
    declare buffer threshold
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog via REST
        anylog_configs:dict - Anylog configurations
        exception:bool - whether to print exception or not
    """
    if 'threshold_time' not in anylog_configs:
        anylog_configs['threshold_time'] = '60 seconds'
    if 'threshold_volume' not in anylog_configs:
        anylog_configs['threshold_volume'] = '10KB'
    if 'write_immediate' not in anylog_configs:
        anylog_configs['write_immediate'] = False

    if generic_post_calls.set_buffer_threshold(anylog_conn=anylog_conn, db_name=None, table_name=None,
                                               time=anylog_configs['threshold_time'],
                                               volume=anylog_configs['threshold_volume'],
                                               write_immediate=anylog_configs['write_immediate'], view_help=False,
                                               exception=exception) is False:
        print('Notice: Failed to set the buffer threshold')


def enable_streaming(anylog_conn:AnyLogConnector, exception:bool=False):
    """
    set streaming
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog via REST
        exception:bool - whether to print exception or not
    """
    processes = generic_get_calls.get_processes(anylog_conn=anylog_conn, json_format=True, exception=exception)
    if processes['Streamer']['Status'] == 'Not declared':
        if generic_post_calls.enable_streamer(anylog_conn=anylog_conn, exception=exception) is False:
            print('Notice: Failed to enable streaming')


def run_publisher(anylog_conn:AnyLogConnector, anylog_configs:dict, exception:bool=False)->bool:
    """
    execute `run publisher`
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog via REST
        anylog_configs:dict - Anylog configurations
        exception:bool - whether to print exception or not
    :prams:
        status:bool
    :return:
        status
    """
    status = True
    if 'watch_dir' not in anylog_configs:
        anylog_configs['watch_dir'] = None
    if 'bkup_dir' not in anylog_configs:
        anylog_configs['bkup_dir'] = None
    if 'error_dir' not in anylog_configs:
            anylog_configs['error_dir'] = None

    if 'dbms_file_location' not in anylog_configs:
        anylog_conn['dbms_file_location'] = 'file_name[0]'
    if 'table_file_location' not in anylog_configs:
        anylog_conn['table_file_location'] = 'file_name[1]'
    if 'publisher_compress_file' not in anylog_configs:
        anylog_configs['publisher_compress_file'] = True
    if 'ledger_conn' not in anylog_configs:
        anylog_configs['ledger_conn'] = None

    processes = generic_get_calls.get_processes(anylog_conn=anylog_conn, json_format=True, exception=exception)
    if processes['Publisher']['Status'] == 'Not declared':
        status = generic_post_calls.run_publisher(anylog_conn=anylog_conn, db_name=anylog_configs['dbms_file_location'],
                                                  table_name=anylog_configs['table_file_location'],
                                                  watch_dir=anylog_configs['watch_dir'], bkup_dir=anylog_configs['bkup_dir'],
                                                  error_dir=anylog_configs['error_dir'], delete_json=False,
                                                  delete_sql=True, compress_json=anylog_configs['publisher_compress_file'],
                                                  compress_sql=False, ledger_conn=anylog_configs['ledger_conn'],
                                                  view_help=False, exception=exception)
        if status is False:
            print(f'Failed to start publisher node')

    return status