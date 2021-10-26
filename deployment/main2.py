import argparse
from importlib.util import find_spec
import os

import __init__
import config
import docker_calls


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


def deploy_docker(config_data:dict, password:str, anylog_update:bool=False, anylog:bool=False, psql:bool=False, grafana:bool=False,
                  exception:bool=False):
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
        if fails to deploy an AnyLog container return False, else return True
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
                                                       rest_port=config_data['anylog_tcp_port'],
                                                       broker_port=config_data['broker_port'],
                                                       authentication=config_data['authentication'],
                                                       username=config_data['username'],
                                                       password=config_data['password'],
                                                       exception=exception):
                status = False
                print('Failed to deploy AnyLog container')

    return status


def main():
    """
    Process:
        1. Read config file
        2. Start AnyLog, Grafana, PSQL if valid
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Send REST requests to configure an AnyLog instance.')
    parser.add_argument('config_file', type=str, default='$HOME/AnyLog-API/config/single-node.ini', help='AnyLog INI config file')
    # Docker configs
    parser.add_argument('--docker-password', type=str, default=None, help='password for docker to download/update AnyLog')
    parser.add_argument('--anylog', type=bool, nargs='?', const=True, default=False, help='deploy AnyLog docker container')
    parser.add_argument('--psql', type=bool, nargs='?', const=True, default=False, help='deploy postgres docker container if db type is `psql` in config')
    parser.add_argument('--grafana', type=bool, nargs='?', const=True, default=False, help='deploy Grafana if `query` in node_type')
    parser.add_argument('--update-anylog', type=bool, nargs='?', const=True, default=False, help='Update AnyLog build')

    # Other
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='print exception errors')
    args = parser.parse_args()

    # Initial config
    config_data = inital_config(config_file=args.config_file)

    # deploy docker packages
    if find_spec('docker'): 
        if not deploy_docker(config_data=config_data, password=args.docker_password, anylog_update=args.update_anylog,
                             anylog=args.anylog, psql=args.psql, grafana=args.grafana, exception=args.exception):
            print('Failed to deploy AnyLog, cannot continue...')
    else:
        print('Unable to deploy docker packages. Missing `docker` module.')
        exit(1)


if __name__ == '__main__':
    main()

