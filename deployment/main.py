import argparse
import datetime
import os
import time

import __init__
import anylog_api
import blockchain_cmd
import clean_node
import config
import dbms_cmd
import docker_calls
import get_cmd
import master
import operator_node
import post_cmd
import publisher
import query
import single_node


def initial_config(config_file:str, exception:bool=False)->(dict,list):
    """
    Extract information from config_file
    :args:
        config_file:str - path to configuration file
        exception:bool - whether to print exceptions
    :params:
        config_data:dict - content from config_file
        node_types:list - list of node types from config_data
    :return:
        config_data & node_types - if incomplete configs program stops

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

    for param in ['external_ip', 'ip', 'anylog_broker_port', 'username', 'password', 'auth_type']:
        if param not in config_data:
            config_data[param] = None
    if 'authentication' not in config_data:
        config_data['authentication'] = 'off'

    node_types = config_data['node_type'].split(',')
    if len(node_types) == 1:
        config_data['node_type'] = node_types[0]
    else:
        config_data['node_type'] = 'single_node'
        if 'publisher' in node_types and 'operator' in node_types:
            node = input("A 'solo deployment' can only have either operator or publisher process on a given container. Would you like operator or publisher? ")
            while node.lower() not in ['operator', 'publisher']:
                node = input('Invalid option: %s. Would you like to run an operator or publisher process? ')
            if node == 'publisher':
                node_types.remove('operator')
            else:
                node_types.remove('publisher')

    # validate node types
    for node in node_types:
        if node not in ['master', 'publisher', 'operator', 'query']:
            if exception is True:
                print("Node type %s isn't supported - supported node types: 'master', 'operator', 'publisher','query'." % node)
            if len(node_types) == 1:
                print("Cannot continue due to an invalid node type '%s'..." % node)
                exit(1)
            else:
                node_types.remove(node)
                if exception is True:
                    print("Removing node type '%s' from config list" % node)

    return config_data, node_types


def deploy_docker(config_data:dict, password:str, update_anylog:bool=False, anylog:bool=False, psql:bool=False,
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
        update_anylog:bool - whether to update the AnyLog docker image
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
        if not docker_conn.deploy_postgres_container(conn_info=config_data['db_user'], exception=exception):
            print('Failed to deploy Postgres docker container, setting db_type to `sqlite`')
            config_data['db_type'] = 'sqlite'

    if grafana is True:
        if not docker_conn.deploy_grafana_container(exception=exception):
            print('Failed to deploy Grafana docker container')

    if anylog is True:
        if not docker_conn.deploy_anylog_container(docker_password=password, update_image=update_anylog,
                                                   container_name=config_data['node_name'], build=config_data['build'],
                                                   external_ip=config_data['external_ip'], local_ip=config_data['ip'],
                                                   server_port=config_data['anylog_tcp_port'],
                                                   rest_port=config_data['anylog_rest_port'],
                                                   broker_port=config_data['anylog_broker_port'],
                                                   authentication=config_data['authentication'],
                                                   auth_type=config_data['auth_type'], username=config_data['username'],
                                                   password=config_data['password'], exception=exception):
            status = False
        else:
            time.sleep(30)

    return status, config_data


def update_config(conn:anylog_api.AnyLogConnect, config_data:dict, upload_config:bool=False,
                  exception:bool=False)->dict:
    """
    Update the config_data object to contain information from within AnyLog dictionary.
    If update_config is set to True, update the AnyLog dictionary
    :args:
        conn:anylog_api.AnyLogConnect - REST connection into AnyLog
        config_data:dict - configs from config_file
        upload_config:bool - whether to upload the config_data into AnyLog dictionary
        exception:bool - whether to print exceptions
    :params:
        dict_config:dict - configuration from AnyLog dictionary
    :return:
        config_data - updated config_data with dict_config
    """
    config_data['hostname'] = get_cmd.get_hostname(conn=conn, exception=exception)

    # Update config_data with info from AnyLog dictionary.
    # If dictionary value differs from config_data value, then config_data gets kept
    dict_config = config.import_config(conn=conn, exception=exception)
    if dict_config != {}:
        if config_data['external_ip'] is None:
            config_data['external_ip'] = dict_config['external_ip']
        if config_data['ip'] is None:
            config_data['ip'] = dict_config['ip']
        if 'anylog_broker_port' not in config_data: 
            config_data['anylog_broker_port'] = None
        if 'authentication' not in config_data: 
            config_data['authentication'] = 'off' 
        if config_data['authentication'] == 'off': 
            config_data['auth_type'] = None 
            config_data['username'] = None
            config_data['password'] = None 

        config_data = {**dict_config, **config_data}

    if upload_config is True:
        if not config.post_config(conn=conn, config=config_data, exception=exception):
            print('Failed to update configs in AnyLog dictionary')

    return config_data


def deploy_anylog(conn:anylog_api.AnyLogConnect, config_data:dict, node_types:list, disable_location:bool=False,
                  deployment_file:str=None, exception:bool=False)->bool:
    """
    Deploy AnyLog instance based on configs
    :process:
        1. connect to system_query database
        2. Start scheduler 1
        3. if set deploy AnyLog script file
        4. run blockchain sync every 30 seconds
        5. start any AnyLog instance based on node_type
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

    # configure system_query to run against SQLite if node type doesn't contain query node
    dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
    if config_data['node_type'] != 'query' and 'query' not in node_types:
        if 'system_query' not in dbms_list:
            if not dbms_cmd.connect_dbms(conn=conn, config={}, db_name='system_query', exception=exception):
                print('Failed to deploy system_query against %s node' % config['node_type'])

    # run scheduler process 1 (and 0)  
    for schedule in [0, 1]:
        if get_cmd.get_scheduler(conn=conn, scheduler_name=schedule, exception=exception) == 'not declared':
            if not post_cmd.start_exitings_scheduler(conn=conn, scheduler_id=schedule, exception=exception):
                print('Failed to start scheduler %s' % schedule)

    # run blockchain sync  
    blockchain_cmd.blockchain_sync_scheduler(conn=conn, source='master', time="30 seconds", master_node=config_data['master_node'], exception=exception)

    # execute deployment file
    if deployment_file is not None:
        full_path = os.path.expandvars(os.path.expanduser(deployment_file))
        if os.path.isfile(full_path) and deployment_file is not None:
            file_deployment.deploy_file(conn=conn, deployment_file=full_path)
        elif deployment_file is not None:
            print("File: '%s' does not exist" % full_path)

    # Start an AnyLog process for a specific node_type
    if 'master' in node_types: 
        config_data['node_type'] = 'master'
        status = master.master_init(conn=conn, config=config_data, disable_location=disable_location, exception=exception)

    for node in sorted(node_types): 
        config_data['node_type'] = node
        if node == 'operator':
            status = operator_node.operator_init(conn=conn, config=config_data, disable_location=disable_location,
                                                 exception=exception)
        elif node == 'publisher':
            status = publisher.publisher_init(conn=conn, config=config_data, disable_location=disable_location,
                                              exception=exception)
        elif node == 'query':
            status = query.query_init(conn=conn, config=config_data, disable_location=disable_location,
                                      exception=exception)
        elif node != 'master':
            print('Unsupported node type: %s' % node) 
            if len(node_types) == 1: 
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


def clean_process(conn:anylog_api.AnyLogConnect, config_data:dict, node_types:dict,
                  anylog:bool=False, rm_policy:bool=False, rm_data:bool=False, anylog_rm_volume:bool=False,
                  anylog_rm_image:bool=False, psql:bool=False, psql_rm_volume:bool=False, psql_rm_image:bool=False,
                  grafana:bool=False, grafana_rm_volume:bool=False, grafana_rm_image:bool=False,
                  exception:bool=False):
    """
    Process to clean AnyLog and disconnect docker instances
    :process:
        1. if set remove policy
        2. stop processes
        3. disconnect database(s) and if set remove them
        4. disconnect container
        5. if remove_data is set, remove correlated data volume
        6. if remove_image is set remove correlated image
    repeat for AnyLog, PSQL and Grafana
    :args:
        conn:anylog_api.AnyLogConnect - REST connection to AnyLog
        config_data:dict - node configuration
        node_types:list - list of node types from config_data
        anylog:bool - whether to disconnect AnyLog docker container
        rm_policy:bool - remove policy / policies correlated to node 
        rm_data:bool - remove data from database(s) within node
        anylog_rm_volume:bool - remove AnyLog related volumes
        anylog_rm_image:bool - remove AnyLog image 
     
        psql:bool - whether to disconnect Postgres docker container
        psql_rm_volume:bool - remove Postgres related volume 
        psql_rm_image:bool - remove Postgres image 
        
        grafana:bool - whether to disconnect Grafana docker container
        grafana_rm_volume:bool - remove Grafana related volumes 
        grafana_rm_image:bool - remove Grafana related image   
    :params:
        docker_conn:docker_calls.DeployAnyLog - connection to docker
    """
    status = True
    docker_conn = docker_calls.DeployAnyLog(exception=exception)

    if anylog is True and docker_conn.validate_container(container_name=config_data['node_name']) is not None:
        # disconnect processes in running node running
        clean_node.disconnect_node(conn=conn, exception=exception)

        # remove policy if set
        clean_node.remove_policy(conn=conn, config_datac=config_data, node_types=node_types, exception=exception)

        # disconnect from database & remove data if set
        clean_node.disconnect_dbms(conn=conn, drop_data=rm_data, config_data=config_data, exception=exception)

        # stop AnyLog container
        if not docker_conn.stop_anylog_container(container_name=config_data['node_name'], build=config_data['build'],
                                                   remove_volume=anylog_rm_volume, remove_image=anylog_rm_image,
                                                   exception=exception):
            print('Failed to stop and/or remove AnyLog')

    if psql is True:
        if not docker_conn.stop_postgres_container(remove_volume=psql_rm_volume, remove_image=psql_rm_image,
                                                   exception=exception):
            print('Failed to stop and/or remove Postgres')

    if grafana is True:
        if not docker_conn.stop_grafana_container(remove_volume=grafana_rm_volume, remove_image=grafana_rm_image,
                                                  exception=exception):
            print('Failed to stop and/or remove Grafana')



def main():
    """
    The following is intended to help users to easily deploy AnyLog via REST
    :process:
        # Deployment process
        0. Read config file into config_data
        1. If set, deploy docker containers for Postgres, Grafana and AnyLog
        2. Connect to AnyLog API & validate connection

        At this point 2 things can happen:
        Option 1) if set, update clean docker configs
            1. calls clean_node
        Option 2) if set, deploy AnyLog instance
            1. Update config_data with information from AnyLog dictionary
            2. Deploy a type of AnyLog node type via REST based on configurations
    :positional arguments:
        rest_conn             REST connection information
        config_file           AnyLog INI config file
    :optional arguments:
        -h, --help                              show this help message and exit
        # Docker deployment process
        --docker-password       DOCKER_PASSWORD     password for docker to download/update AnyLog                       (default: None)
        --anylog                ANYLOG              deploy AnyLog docker container                                      (default: False)
        --psql                  PSQL                deploy postgres docker container if db type is `psql` in config     (default: False)
        --grafana               GRAFANA             deploy Grafana if `query` in node_type                              (default: False)
        --update-anylog         UPDATE_ANYLOG       Update AnyLog build                                                 (default: False)
        # Discocnnect docker container(s)
        --disconnect-anylog     DISCONNECT_ANYLOG   stop AnyLog docker instance     (default: False)
        --disconnect-psql       DISCONNECT_PSQL     stop Postgres docker instance   (default: False)
        --disconnect-grafana    DISCONNECT_GRAFANA  stop Grafana docker instance    (default: False)
        --remove-policy         REMOVE_POLICY       remove policy from ledger that's not of type 'cluster' or 'table' correlated to the node (default: False)
        --remove-data           REMOVE_DATA         remove data from database in the correlated attached node (default: False)
        --remove-volume         REMOVE_VOLUME       remove AnyLog volumes correlated to the attached node (default: False)
        # Other parameters
        -t,  --timeout              TIMEOUT             REST timeout period (default: 30)
        -c,  --update-config        UPDATE_CONFIG       Update information from config_file into AnyLog dictionary (default: False)
        -dl, --disable-location     DISABLE_LOCATION     Whether to disable location when adding a new node policy to the ledger (default: False)
        -e,  --exception            EXCEPTION            print exception errors (default: False)
    :params:
        anylog_conn:anylog_api.AnyLogConnect - connection to AnyLog API
        config_data:dict - data from config_file
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Send REST requests to configure an AnyLog instance.')
    parser.add_argument('rest_conn',   type=str, default=__get_rest_conn(),                         help='REST connection information')
    parser.add_argument('config_file', type=str, default='$HOME/AnyLog-API/config/single-node.ini', help='AnyLog INI config file')

    # Docker configs
    parser.add_argument('--docker-password', type=str,  default=None, help='password for docker to download/update AnyLog')
    parser.add_argument('--docker-only',     type=bool, nargs='?', const=True, default=False, help='If set, code will not continue once docker instances are up')
    parser.add_argument('--full-deployment', type=bool, nargs='?', const=True, default=False, help='Update & connect to AnyLog, PSQL and Grafana containers')
    parser.add_argument('--anylog',          type=bool, nargs='?', const=True, default=False, help='deploy AnyLog docker container')
    parser.add_argument('--psql',            type=bool, nargs='?', const=True, default=False, help='deploy postgres docker container if db type is `psql` in config')
    parser.add_argument('--grafana',         type=bool, nargs='?', const=True, default=False, help='deploy Grafana if `query` in node_type')
    parser.add_argument('--update-anylog',   type=bool, nargs='?', const=True, default=False, help='Update AnyLog build')

    # Clean up
    parser.add_argument('--full-clean',         type=bool, nargs='?', const=True, default=False, help='Remove everything AnyLog related from machine')
    parser.add_argument('--disconnect-anylog',  type=bool, nargs='?', const=True, default=False, help="stop AnyLog docker instance")
    parser.add_argument('--rm-policy',          type=bool, nargs='?', const=True, default=False, help="remove policy from ledger that's not of type 'cluster' or 'table' correlated to the node")
    parser.add_argument('--rm-data',            type=bool, nargs='?', const=True, default=False, help="remove data from database in the correlated attached node")
    parser.add_argument('--anylog-rm-volume',   type=bool, nargs='?', const=True, default=False, help="remove AnyLog volumes correlated to the attached node")
    parser.add_argument('--anylog-rm-image',    type=bool, nargs='?', const=True, default=False, help="remove AnyLog image")
    parser.add_argument('--disconnect-psql',    type=bool, nargs='?', const=True, default=False, help="stop Postgres docker instance")
    parser.add_argument('--psql-rm-volume',     type=bool, nargs='?', const=True, default=False, help="remove Postgres volume")
    parser.add_argument('--psql-rm-image',      type=bool, nargs='?', const=True, default=False, help="remove AnyLog volumes correlated to the attached node")
    parser.add_argument('--disconnect-grafana', type=bool, nargs='?', const=True, default=False, help="stop Grafana docker instance")
    parser.add_argument('--grafana-rm-volume',  type=bool, nargs='?', const=True, default=False, help="remove Grafana volumes")
    parser.add_argument('--grafana-rm-image',   type=bool, nargs='?', const=True, default=False, help="remove Grafana image")

    # Other
    parser.add_argument('-t',  '--timeout',          type=int,  default=30,   help='REST timeout period')
    parser.add_argument('-c',  '--upload-config',    type=bool, nargs='?',    const=True, default=False, help='Update information from config_file into AnyLog dictionary')
    parser.add_argument('-dl', '--disable-location', type=bool, nargs='?',    const=True, default=False, help='Whether to disable location when adding a new node policy to the ledger')
    parser.add_argument('-df', '--deployment-file',  type=str,  default=None, help='An AnyLog file user would like to deploy in addition to the configurations') 
    parser.add_argument('-e',  '--exception',        type=bool, nargs='?',    const=True, default=False, help='print exception errors')
    args = parser.parse_args()

    if args.full_deployment is True:
        args.anylog = True
        args.psql = True
        args.grafana = True
        args.update_anylog = True
    elif args.update_anylog is True:
        args.anylog = True

    if args.full_clean is True:
        args.disconnect_anylog = True
        args.anylog_rm_volume = True
        args.anylog_rm_image = True
    elif args.rm_policy is True or args.rm_data is True or args.anylog_rm_volume is True or args.anylog_rm_image is True:
        args.disconnect_anylog = True
    if args.full_clean is True:
        args.disconnect_psql = True
        args.psql_rm_volume = True
        args.psql_rm_image = True
    elif args.psql_rm_volume is True or args.psql_rm_image is True:
        args.disconnect_psql = True
    if args.full_clean is True:
        args.disconnect_grafana = True
        args.grafana_rm_volume = True
        args.grafana_rm_image = True
    elif args.grafana_rm_volume is True or args.grafana_rm_image is True:
        args.disconnect_grafana = True

    # Initial config
    config_data, node_types = initial_config(config_file=args.config_file)
    
    # Set up connection to AnyLog via REST
    anylog_conn = anylog_api.AnyLogConnect(conn=args.rest_conn, auth=(), timeout=args.timeout)
    if config_data['authentication'] == 'on' and 'username' in config_data and 'password' in config_data:
        anylog_conn = anylog_api.AnyLogConnect(conn=args.rest_conn, auth=(config_data['username'],
                                                                          config_data['password']),
                                               timeout=args.timeout)

    # connect or disconnect to nodes:
    if args.anylog is True or args.psql is True or args.grafana is True:
        if not deploy_docker(config_data=config_data, password=args.docker_password, update_anylog=args.update_anylog, anylog=args.anylog,
                      psql=args.psql, grafana=args.grafana, exception=args.exception):
            error = 'Failed to deploy AnyLog docker container.'
            if args.docker_only is False:
                args.docker_only = True
                error += ' Unable to start node of type: %s' % config_data['node_type']
            print(error)
    elif args.disconnect_anylog is True or args.disconnect_psql is True or args.disconnect_grafana is True:
        clean_process(conn=anylog_conn, config_data=config_data, node_types=node_types, anylog=args.disconnect_anylog,
                      rm_policy=args.rm_policy, rm_data=args.rm_data, anylog_rm_volume=args.anylog_rm_volume,
                      anylog_rm_image=args.anylog_rm_image, psql=args.disconnect_psql,
                      psql_rm_volume=args.psql_rm_volume, psql_rm_image=args.psql_rm_image,
                      grafana=args.disconnect_grafana, grafana_rm_volume=args.grafana_rm_volume,
                      grafana_rm_image=args.grafana_rm_image, exception=args.exception)
        exit(1)

    # validate node is accessible
    if args.anylog is True:
        if not get_cmd.get_status(conn=anylog_conn, exception=args.exception):
            print('Failed to get status from %s, cannot continue' % anylog_conn.conn)
            exit(1)

    #  Update config_data & deploy AnyLog
    if args.docker_only is False:
        config_data = update_config(conn=anylog_conn, config_data=config_data, upload_config=args.upload_config,
                                    exception=args.exception)

        deploy_anylog(conn=anylog_conn, config_data=config_data, node_types=node_types,
                      disable_location=args.disable_location, deployment_file=args.deployment_file,
                      exception=args.exception)



if __name__ == '__main__':
    main()
