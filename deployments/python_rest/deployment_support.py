import argparse
import re

from anylog_connector import AnyLogConnector
import blockchain_calls
import find_location
import generic_get_calls
import generic_post_calls

from file_io import read_configs
from support import dictionary_merge


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


def anylog_connection(rest_conn:str, timeout:int)->AnyLogConnector:
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

    return AnyLogConnector(conn=conn, auth=auth, timeout=timeout)


def set_dictionary(anylog_conn:AnyLogConnector, config_file:str, exception:bool=False)->dict:
    """
    Merge configuration file and default dictionary inoto a single dictionary
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog via REST
        config_file:str - configuration file
        exception:bool - whether to print exceptions
    :params:
        file_configuration:dict - configuration from file
        anylog_configuration:dict - configuration from anylog
        configs:dict - merged configurations (file_configuration is "default")
    :return:
        configs
    """
    file_configuration = read_configs(config_file=config_file, exception=exception)
    anylog_configuration = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, view_help=False, exception=exception)
    anylog_configuration['hostname'] = generic_get_calls.get_hostname(anylog_conn=anylog_conn, view_help=False, exception=exception)

    configs = dictionary_merge(file_config=file_configuration, anylog_config=anylog_configuration)

    return configs


def set_license_key(anylog_conn:AnyLogConnector, license_key:str, exception:bool=False):
    """
    set license key
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        license_key:str - License key
        exception:bool - whether to print exceptions
    :params:
        count:int - counter
        is_license:bool - whether license exists or not
    """
    count = 0

    is_license = generic_get_calls.get_license(anylog_conn=anylog_conn, view_help=False, exception=exception)
    if is_license is False and (license_key is None or license_key == ''):
        print("License Key not provided, cannot continue setting up the node")
        exit(1)

    while is_license is False and count < 2:
        generic_post_calls.activate_license_key(anylog_conn=anylog_conn, license_key=license_key,
                                                exception=exception)
        is_license = generic_get_calls.get_license(anylog_conn=anylog_conn, view_help=False, exception=exception)
        count += 1

    if is_license is False:
            print(f"Failed to set AnyLog license with license: {license_key}")
            exit(1)
    else:
        print("AnyLog has been activated")


def set_synchronizer(anylog_conn:AnyLogConnector, configuration:dict, exception:bool):
    """
    Enable blockchain sync
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog via REST
        configuration:dict - node configuration
        exception:bool - whether to print exceptions
    :params:
        counter:int
        blockchain_source:str - source where data is coming from (default: master node)
        blockchain_destination:str - destination where data will be stored locally (default: file)
        sync_time:str - how often to sync
        ledger_conn:str - connection to blockchain ledger (for master use IP:Port)
        processes:dict - `get processes` results
    """
    counter = 0
    blockchain_source = 'master'
    if 'blockchain_source' in configuration:
        blockchain_source = configuration['blockchain_source']
    blockchain_destination='file'
    if 'blockchain_destination' in configuration:
        blockchain_destination = configuration['blockchain_destination']
    sync_time='30 seconds'
    if 'sync_time' in configuration:
        sync_time = configuration['sync_time']
    ledger_conn = f"127.0.0,1:32048"
    if 'ledger_conn' in configuration:
        ledger_conn = configuration['ledger_conn']
    elif 'anylog_server_port' in configuration:
        ledger_conn=f"127.0.0.1:{configuration['anylog_server_port']}"

    processes = generic_get_calls.get_processes(anylog_conn=anylog_conn, json_format=True, view_help=False, exception=exception)
    while processes['Blockchain Sync']['Status'] == 'Not declared' and counter < 2:
        blockchain_calls.blockchain_sync(anylog_conn=anylog_conn, blockchain_source=blockchain_source,
                                         blockchain_destination=blockchain_destination, sync_time=sync_time,
                                         ledger_conn=ledger_conn, view_help=False, exception=exception)
        processes = generic_get_calls.get_processes(anylog_conn=anylog_conn, json_format=True, view_help=False,
                                                    exception=exception)
        counter += 1

    if processes['Blockchain Sync']['Status'] == 'Not declared':
        print(f"Failed to enable blockchain sync")


def node_location(anylog_conn:AnyLogConnector, configs:dict, exception:bool=False)->(str, str, str, str):
    """
    Validate if user has defined the location of a node in configuration. If not then use the coordinates generated via
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog via REST
        configs:dict - AnyLog configurations
        exception:bool - whether to print exceptions
    :params:
        location_params:dict - node based location
        location:str - coordinates
        country:str
        state:str
        city:str
    """
    location_params = find_location.get_location(anylog_conn=anylog_conn, exception=exception)

    if 'location' in configs:
        location = configs['location']
    else:
        location = location_params['location']
    if 'country' is configs:
        country = configs['country']
    else:
        country = location_params['country']
    if 'state' in configs:
        state = configs['state']
    else:
        state = location_params['state']
    if 'city' in configs['city']:
        city = configs['city']
    else:
        city = location_params['city']

    return location, country, state, city