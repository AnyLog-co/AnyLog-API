import os
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).rsplit('deployment', 1)[0]
rest_dir = os.path.join(ROOT_PATH, 'rest')
support_dir = os.path.join(ROOT_PATH, 'support')
sys.path.insert(0, support_dir)

try:
    from docker_api import DeployDocker
except:
    pass

def deploy_anylog_container(env_params:dict, docker_only:bool=False, docker_update:bool=False,
                            docker_password:str=None, exception:bool=True):
    """
    Deploy AnyLog container
    :args:
        env_params:dict - parameters from config_file
        docker_only:bool - whether to deploy docker only or continue to REST requests
        docker_update:bool - whether to update AnyLog image
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
        none
    """
    # {'general': {'build': 'predevelop', 'node_type': 'none', 'node_name': 'new-node', 'company_name': 'Your Company Name'}, 'authentication': {'authentication': 'true', 'username': 'ori', 'password': 'gAAAAABhvOWrY9fUHVdvCVUX3HQPyCODvIpV_tMTf0HwR0NfPnl1BFba_xT3XQubg7_xmhC-htbUPPZ9RSFe2JEthdaahIYDYg==', 'auth_type': 'admin'}, 'database': {'db_type': 'sqlite', 'db_port': '5432', 'db_user': 'db_user@127.0.0.1:gAAAAABhvOWrgnn-zE7yN8Jc3orzLuHgTPjW-B8XIs_SwRLLsn3lgye0WkAVJwIikOyEncbY4yINXEqPGWDCZThZzXy_Y5zlpw=='}}
    
    build = env_params['build']
    node_type = env_params[node_type]
    node_name = env_params['node_name']
    master_node = env_params['master_node']
    auth_params = {
        'authentication': 'off',
        'username': '',
        'password': '',
        'auth_type': ''
    }

    if docker_only is False:
        node_type = 'rest'


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
    :return:
        none
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


def deploy_grafana(exception:bool=True)->bool:
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