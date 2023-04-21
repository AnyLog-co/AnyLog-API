import argparse
import json
import re

import file_io

import anylog_connector
import database
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
    anylog_configs = generic_get.get_dictionary(anylog_conn=anylog_conn, json_format=True, view_help=False)
    configs = file_io.read_configs(config_file=config_file, exception=exception)

    for config in anylog_configs:
        if config not in configs:
            configs[config] = anylog_configs[config]

    return configs


def serialize_row(data:dict):
    """
    Serialize data
    :args:
        data:dict - content to serialize
    :return:
        dict as JSON string(s)
    """
    try:
        return json.dumps(data)
    except Exception as error:
        print(f"Failed to serialize data")

def check_synchronizer(anylog_conn:anylog_connector.AnyLogConnector):
    """
    Check whether blockchain synchronizer is active
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog via REST
    :params:
        status:bool
    :return:
        True if blockchain sync is active
        False if not
    """
    status = False
    active_processes = generic_get.get_processes(anylog_conn=anylog_conn, json_format=True)
    if "Blockchain Sync" in active_processes and "Status" in active_processes["Blockchain Sync"]:
        if active_processes["Blockchain Sync"]["Status"] != "Not declared":
            status = True

    return status


def connect_dbms(anylog_conn:anylog_connector.AnyLogConnector, db_name:str, configurations:dict, execute_cmd:bool=True):
    """
    Connect to logical (SQL) database
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - Connecton to AnyLog node
        db_name:str - logical database
        configurations:dict - AnyLog configurations
    :params:
        ip:str - IP address for connecting to database
        port:int - database port
        user:str - username recognized by the database
        password;str - user dbms password
        memory:bool - whether database is in memory or not (usually with SQLite)
    :return:
        True if Success
        False if fails
    """
    ip = None
    port = None
    user = None
    password = None
    memory = False

    if 'db_ip' in configurations:
        ip = configurations["db_ip"]
    if 'db_port' in configurations:
        port = configurations["db_port"]
    if 'db_user' in configurations:
        user = configurations['db_user']
    if 'db_password' in configurations:
        password = configurations['db_password']
    if 'memory' in configurations:
        memory = configurations['memory']

    return database.connect_dbms(anylog_conn=anylog_conn, db_name=db_name, db_type=configurations['db_type'],
                                 ip=ip, port=port, user=user, password=password, memory=memory, execute_cmd=execute_cmd,
                                 view_help=False)


def build_where_condition(configuration:dict):
    where_conditions = {
        "name": configuration['node_name'],
        "company": configuration['company_name'],
        "port": configuration['anylog_server_port'],
        "rest_port": configuration['anylog_rest_port']
    }

    if "tcp_bind" in configuration and configuration["tcp_bind"] is False:
        where_conditions["ip"] = configuration["external_ip"]
        where_conditions["local_ip"] = configuration["ip"]
    elif "tcp_bind" in configuration and configuration["tcp_bind"] is False:
        where_conditions["external_ip"] = configuration["external_ip"]
        where_conditions["ip"] = configuration["ip"]

    return where_conditions
