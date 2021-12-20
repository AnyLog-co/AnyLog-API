import os
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).rsplit('deployment', 1)[0]
rest_dir = os.path.join(ROOT_PATH, 'rest')
support_dir = os.path.join(ROOT_PATH, 'support')
sys.path.insert(0, support_dir)

import io_configs

try:
    from docker_api import DeployDocker
except:
    pass


def deploy_anylog_container(env_configs:dict, docker_only:bool=False, update_anylog:bool=False,
                            docker_password:str=None, exception:bool=True):
    """
    Deploy AnyLog container
    :args:
        env_configs:dict - parameters from config_file
        docker_only:bool - whether to deploy docker only or continue to REST requests
        update_anylog:bool - whether to update AnyLog image
        docker_password:str - docker password
        exception:bool - whether to print exceptions
    :params:
        status:bool
        deploy_docker:docker_api.DeployDocker - call to DeployDocker class
        env_param configs
            * build:str - AnyLog docker image build
            * node_type:str - node type
            * node_name:str - node name
            * networking_parms

            * auth_params:dict - authentication params
            * db_params:dict - database params
            * operator_params:dict - params related to operator
            * mqtt_params:dict - params related to MQTT

    :print:
        when exception is True, print whether AnyLog was deployed properly or not
    :return:
        status
    """
    try: 
        build = env_configs['general']['build']
    except: 
        build = "predevelop"
    try: 
        node_type = env_configs['general']['node_type']
    except:
        node_type = "none"
    else: 
        if docker_only is False and node_type != 'none':
            node_type = 'rest'
    try:
        node_name = env_configs['general']['node_name']
    except:
        node_name = 'new-node'

    env_params = io_configs.format_configs(env_configs=env_configs)
    env_params['NODE_TYPE'] = node_type

    deploy_docker = DeployDocker()
    status = deploy_docker.deploy_anylog_container(build=build, node_name=node_name, environment_variables=env_params,
                                                   docker_password=docker_password, update_anylog=update_anylog)
    if exception is True:
        if status is True:
            print('Successfully deployed AnyLog container node of type: %s' % node_type)
        else:
            print('Failed to deploy AnyLog container node of type: %s' % node_type)

    return status


def deploy_postgres(env_params:dict, exception:bool=True):
    """
    Deploy Postgres Instance
    :args:
        env_params:dict - configuration params
        exception:bool - whether to print exceptions
    :params:
        status:bool
        username:str - postgres username
        password:str - postgres password
        deploy_docker:docker_api.DeployDocker - call to DeployDocker class
    :print:
        when exception is True, print whether postgres was deployed properly or not
    """
    username = 'anylog'
    password = 'demo'
    if 'db_user' in env_params:
        if '@' in env_params['db_user']:
            username = env_params['db_user'].split('@')[0]
        if ':' in env_params['db_user']:
            password = env_params['db_user'].split(':')[-1]

    deploy_docker = DeployDocker()

    status = deploy_docker.deploy_postgres_container(username=username, password=password)
    if exception is True:
        if status is True:
            print('Successfully deployed Postgres container')
        else:
            print('Failed to deploy Postgres container')


def deploy_grafana(exception:bool=True):
    """
    Deploy Grafana instance
    :args:
        exception:bool - whether to print exceptions
    :params:
        status:bool
        deploy_docker:docker_api.DeployDocker - call to DeployDocker class
    :print:
        when exception is True, print whether grafana was deployed properly or not
    :return:
        none
    """
    deploy_docker = DeployDocker()

    status = deploy_docker.deploy_grafana_container()
    if exception is True:
        if status is True:
            print('Successfully deployed Grafana container')
        else:
            print('Failed to deploy Grafana container')
