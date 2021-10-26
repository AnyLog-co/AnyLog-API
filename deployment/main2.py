import argparse
from importlib.util import find_spec
import os
import socket

import __init__
import anylog_api
import config
import docker_calls
import get_cmd
import master
import operator_node
import publisher
import query
import single_node


def __get_rest_conn()->str:
    """
    Get IP address of node
    :params:
        ip_addr:str - IP address
    :return:
        ip_addr
    """
    ip_addr = '127.0.0.1'
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            try:
                sock.connect(("8.8.8.8", 80))
            except:
                pass
            else:
                try:
                    ip_addr = sock.getsockname()[0]
                except:
                    pass
    except:
        pass
    else:
        ip_addr = '%s:2049' % ip_addr

    return ip_addr


def inital_config(config_file:str)->dict:
    """
    Extract information from config_file
    :args:
        config_file:str - path to configuration file
    :params:
        config_data:dict - content from config_file
    :return:
        config_data - if incomplete configs program stops
    """
    config_file = os.path.expandvars(os.path.expanduser(config_file))
    if not os.path.isfile(config_file):
        print('Failed to locate config file: %s, cannot continue...' % args.config_file)
        exit(1)
    config_data = config.read_config(config_file)
    if config_data == {}:
        print('Failed to extract configs from file: %s, cannot continue...' % config_file)
        exit(1)
    elif not config.validate_config(config=config_data):
        print('Missing one or more required config parameters...')
        exit(1)

    for param in ['external_ip', 'local_ip', 'broker_port', 'username', 'password']:
        if param not in config_data:
            config_data[param] = None
    if 'authentication' not in config_data:
        config_data['authentication'] = 'off'

    return config_data


def deploy_docker(config_data:dict, password:str, anylog_update:bool=False, anylog:bool=False, psql:bool=False,
                  grafana:bool=False, exception:bool=False)->(bool, dict):
    """
    Deploy docker instances
    :process:
        1. Deploy Postgres
        2. Deploy Grafana
        3. Update AnyLog if valid
        4. Deploy AnyLog
    Note: On first iteration docker automatically pulls image(s) from hub
    :args:
        anylog_update:bool - whether to update the AnyLog docker image
        anylog:bool - deploy AnyLog
        psql:bool - deploy postgres image version 14.0-alpine
        grafana:bool - deploy grafana image version 7.5.7
        exception:bool - whether to print exceptions
    :params:
        status:bool
        docker_conn:docker_calls.DeployAnyLog  - docker connection
    :return:
        1. status code of whether or not AnyLog was deployed
        2. since the config_data can change (when PSQL fails to start), the "updated' config file
    """
    status = True
    docker_conn = docker_calls.DeployAnyLog(exception=exception)

    if psql is True and config_data['db_type'] == 'psql':
            if not docker_conn.deploy_psql_container(conn_info=config_data['db_user'], db_port=config_data['db_port'],
                                                     exception=exception):
                print('Failed to deploy Postgres docker container, setting db_type to `sqlite`')
                config_data['db_type'] = 'sqlite'

    if grafana is True:
        if not docker_conn.deploy_grafana_container(exception=exception):
            print('Failed to deploy Grafana docker container')

    if anylog_update is True or anylog is True:
        status = docker_conn.docker_login(password=password, exception=exception)
        if status is False:
            print('Failed to log into docker using password: %s' % password)
        if status is True and anylog_update is True:
            if not docker_conn.update_image(build=config_data['build'], exception=exception):
                print('Failed to pull AnyLog docker image')
        if anylog is True:
            status = True
            if not docker_conn.deploy_anylog_container(node_name=config_data['node_name'], build=config_data['build'],
                                                       external_ip=config_data['external_ip'],
                                                       local_ip=config_data['local_ip'],
                                                       server_port=config_data['anylog_tcp_port'],
                                                       rest_port=config_data['anylog_rest_port'],
                                                       broker_port=config_data['anylog_broker_port'],
                                                       authentication=config_data['authentication'],
                                                       username=config_data['username'],
                                                       password=config_data['password'],
                                                       exception=exception):
                status = False
                print('Failed to deploy AnyLog container')

    return status, config_data


def update_config(conn:anylog_api.AnyLogConnect, config_data:dict, update_config:bool=False,
                  exception:bool=False)->dict:
    """
    Update the config_data object to contain information from within AnyLog dictionary.
    If update_config is set to True, update the AnyLog dictionary
    :args:
        conn:anylog_api.AnyLogConnect - REST connection into AnyLog
        config_data:dict - configs from config_file
        update_config:bool - whether to update the config_data into AnyLog dicitonary
        exception:bool - whether to print exceptions
    :params:
        dict_config:dict - configuration from AnyLog dictionary
        node_types:list - list of types of nodes to deploy
    :return:
        config_data - updated config_data with dict_config
    """
    config_data['hostname'] = get_cmd.get_hostname(conn=conn, exception=exception)

    # Update config_data with info from AnyLog dictionary.
    # If dictionary value differs from config_data value, then config_data gets kept
    dict_config = config.import_config(conn=conn, exception=exception)
    if dict_config != {}:
        config_data = {**dict_config, **config_data}

    node_types = config_data['node_type'].split(',')
    if len(node_types) == 1:
        config_data['node_type'] = node_types[0]
    else:
        config_data['node_type'] = 'single_node'
    # validate node types
    for node in node_types:
        if node not in ['master', 'publisher', 'operator', 'query']:
            if exception is True:
                print(("Node type %s isn't supported - supported node types: 'master', 'operator', 'publisher','query'." % node))
            if len(node_types) == 1:
                print("Cannot continue due to an invalid node type '%s'..." % node)
                exit(1)
            else:
                node_types.remove(node)
                if exception is True:
                    print("Removing node type '%s' from config list" % node)

    if update_config is True:
        if not config.post_config(conn=conn, config=config_data, exception=exception):
            print('Failed to update configs into AnyLog dictionary')

    return config_data, node_types


def deploy_anylog(conn:anylog_api.AnyLogConnect, config_data:dict, node_types:list, disable_location:bool=False,
                  exception:bool=False)->bool:
    """
    Deploy AnyLog instance based on configs
    :args:
        conn:anylog_api.AnyLogConnect - REST connection to AnyLog
        config_data:dict - config data from config_file
        node_types:list - node types from config data
        disable_location:bool - Whether to disable location when adding a new node policy to the ledger
        exception:bool - whether to print exceptions
    :params:
        status:bool - used to print whether we deployed AnyLog or not
    """
    status = True
    # Start an AnyLog process for a specific node_type
    if config_data['node_type'] == 'master':
        status = master.master_init(conn=conn, config=config_data, disable_location=disable_location,
                                    exception=exception)
    elif config_data['node_type'] == 'operator':
        status = operator_node.operator_init(conn=conn, config=config_data, disable_location=disable_location,
                                             exception=exception)
    elif config_data['node_type'] == 'publisher':
        status = publisher.publisher_init(conn=conn, config=config_data, disable_location=disable_location,
                                          exception=exception)
    elif config_data['node_type'] == 'query':
        status = query.query_init(conn=conn, config=config_data, disable_location=disable_location,
                                  exception=exception)
    elif config_data['node_type'] == 'single_node':  # a situation where config contains more than one node_type
        status = single_node.single_node_init(conn=conn, config=config_data, node_types=node_types,
                                              disable_location=disable_location, exception=exception)
    else:
        status = False

    if status is False:
        print('Failed to configure %s to act as a %s node type' % (conn.conn, config_data['node_type']))
    else:
        process_list = get_cmd.get_processes(conn=conn, exception=exception)
        if process_list is not None:
            print('A node of type %s was deployed against %s' % (config_data['node_type'], conn.conn))
            print(process_list)
        else:
            print('Unable to get process list as such it is unclear whether a node of type %s was deployed against %s...' % (
                config['node_type'], conn.conn))

def clean_node(node_name:str, anylog:bool=False, psql:bool=False, grafana:bool=False, exception:bool=False):
    """
    Process to clean AnyLog and disconnect docker instances
    :args:
        node_name:str - AnyLog node name
        anylog:bool - whether to disconnect AnyLog docker container
        psql:bool - whether to disconnect PSQL docker container
        grafana:bool - whether to disconnect Grafana docker container
    :params:
        status:bool
    """
    status = True
    docker_conn = docker_calls.DeployAnyLog(exception=exception)
    if anylog is True:
        docker_conn.stop_docker_container(container_name=node_name)
    if psql is True:
        docker_conn.stop_docker_container(container_name='anylog-psql')
    if grafana is True:
        docker_conn.stop_docker_container(container_name='grafana')



def main():
    """
    The following is intended to help users to easily deploy AnyLog via REST
    :process:
        0. Read config file into config_data
        1. If set, deploy docker containers for Postgres, Grafana and AnyLog
        2. Validate connection
        3. Update config_data with values from dictionary & update dictionary if set
    :params:
        anylog_conn:anylog_api.AnyLogConnect - connection to AnyLog API
        config_data:dict - data from config_file
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Send REST requests to configure an AnyLog instance.')
    parser.add_argument('rest_conn',   type=str, default=__get_rest_conn(),                         help='REST connection information')
    parser.add_argument('config_file', type=str, default='$HOME/AnyLog-API/config/single-node.ini', help='AnyLog INI config file')

    # Docker configs
    parser.add_argument('--docker-password', type=str,  default=None, help='password for docker to download/update AnyLog')
    parser.add_argument('--anylog',          type=bool, nargs='?',    const=True, default=False, help='deploy AnyLog docker container')
    parser.add_argument('--psql',            type=bool, nargs='?',    const=True, default=False, help='deploy postgres docker container if db type is `psql` in config')
    parser.add_argument('--grafana',         type=bool, nargs='?',    const=True, default=False, help='deploy Grafana if `query` in node_type')
    parser.add_argument('--update-anylog',   type=bool, nargs='?',    const=True, default=False, help='Update AnyLog build')

    # Clean up
    parser.add_argument('--disconnect-anylog',  type=bool, nargs='?', const=True, default=False, help="stop AnyLog docker instance")
    parser.add_argument('--disconnect-psql',    type=bool, nargs='?', const=True, default=False, help="stop Postgres docker instance")
    parser.add_argument('--disconnect-grafana', type=bool, nargs='?', const=True, default=False, help="stop Grafana docker instance")


    # Other
    parser.add_argument('-t',  '--timeout',          type=int,  default=30, help='REST timeout period')
    parser.add_argument('-c', '--update-config',     type=bool, nargs='?',  const=True, default=False, help='Update information from config_file into AnyLog dictionary')
    parser.add_argument('-dl', '--disable-location', type=bool, nargs='?', const=True, default=False, help='Whether to disable location when adding a new node policy to the ledger')
    parser.add_argument('-e',  '--exception',        type=bool, nargs='?',  const=True, default=False, help='print exception errors')
    args = parser.parse_args()

    # Initial config
    config_data = inital_config(config_file=args.config_file)

    # deploy docker packages
    if find_spec('docker'): 
        status, config_data = deploy_docker(config_data=config_data, password=args.docker_password,
                                            anylog_update=args.update_anylog, anylog=args.anylog, psql=args.psql,
                                            grafana=args.grafana, exception=args.exception)
        if not status:
            print('Failed to deploy AnyLog, cannot continue...')
            exit(1)
    else:
        print('Unable to deploy docker packages. Missing `docker` module.')
        exit(1)

    # Connect to AnyLog REST
    anylog_conn = anylog_api.AnyLogConnect(conn=args.rest_conn, auth=(), timeout=args.timeout)
    if config_data['authentication'] == 'on':
        anylog_conn = anylog_conn.AnyLogConnect(conn=args.rest_conn,
                                                auth=(config_data['username'], config_data['password']),
                                                timeout=args.timeout)

    # Validate connection
    if not get_cmd.get_status(conn=anylog_conn, exception=args.exception):
        print('Failed to get status from %s, cannot continue' % anylog_conn.conn)
        exit(1)

    # Update configs & validate node_type(s)
    config_data, node_types = update_config(conn=anylog_conn, config_data=config_data, update_config=args.update_config,
                                            exception=args.exception)

    if args.disconnect_anylog is False and args.disconnect_psql is False and args.disconnect_grafana is False:
        deploy_anylog(conn=anylog_conn, config_data=config_data, node_types=node_types,
                      disable_location=args.diable_location, exception=args.exception)
    else:
        clean_node(node_name=config_data['node_name'], anylog=args.disconnect_anylog, psql=args.disconnect_psql,
                   grafana=args.disconnect_grafana, exception=args.exception)




if __name__ == '__main__':
    main()

