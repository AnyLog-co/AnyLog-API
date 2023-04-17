import argparse
import os.path
import re

import file_io

import anylog_connector
import generic_get

def validate_conn_pattern(conn:str)->str:
    """
    Validate connection information format is connect
    :valid formats:
        127.0.0.1:32049
        user:passwd@127.0.0.1:32049
    :args:
        conn:str - REST connection information
    :params:
        pattern1:str - compiled pattern 1 (127.0.0.1:32049)
        pattern2:str - compiled pattern 2 (user:passwd@127.0.0.1:32049)
    :return:
        if fails raises Error
        if success returns conn
    """
    pattern1 = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$')
    pattern2 = re.compile(r'^\w+:\w+@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$')

    if not pattern1.match(conn) and not pattern2.match(conn):
        raise argparse.ArgumentTypeError(f'Invalid REST connection format: {conn}')

    return conn


def anylog_connection(rest_conn:str)->(str, tuple):
    """
    Connect to AnyLog node
    :args:
        rest_conn:str - REST connection information
        timeout:int - REST timeout
    :params:
        conn:str - REST IP:Port  from rest_conn
        auth:tuple - REST authentication from rest_conn
    :return:
        connection to AnyLog node
    """
    conn = rest_conn.split('@')[-1]
    auth = None
    if '@' in rest_conn:
        auth = tuple(rest_conn.split('@')[0].split(':'))

    return conn, auth


def prepare_dictionary(anylog_conn:anylog_connector.AnyLogConnector, config_file:str, exception:bool=False):
    """
    Merge anylog dictionary with file configurations
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - Connection to AnyLog via REST
        config_file:str - configuration file
        exception:bool - whether to print exceptions
    :params:
        configs:dict - merged configurations
    :return:
        configs
    """
    configs = {}
    anylog_configs = generic_get.get_dictionary(anylog_conn=anylog_conn, json_format=True, view_help=False)
    file_configs = file_io.read_configs(config_file=config_file, exception=exception)

    for config in anylog_configs:
        if config not in file_configs:
            configs[config] = anylog_configs[config]
        else:
            configs[config] = file_configs[config]

    return configs





