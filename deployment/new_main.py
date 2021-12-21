import argparse
import os
import pkgutil
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).rsplit('deployment', 1)[0]
rest_dir = os.path.join(ROOT_PATH, 'rest')
support_dir = os.path.join(ROOT_PATH, 'support')
sys.path.insert(0, rest_dir)
sys.path.insert(0, support_dir)

import anylog_api
import get_cmd
import io_configs
import docker_deployment as docker
import generic_node

def main():
    """
    The following is intended to provide the ability to deploy docker container(s) based on a configuration file.
    :process:
        1. validate config file exists && docker package is installed (if either is missing exists)
        2. extract content from config_file
        4. deploy PSQL if set
        5. deploy Grafana if set
        6. deploy AnyLog if set
        7. if --docker-only is set, end
        8. if --docker-only is not set execute REST requests based on configs
    :note:
        A node_type of `none` or `rest` will use the code in AnyLog-Network/local_scripts, and will not actually
    execute any additional processes -- such as: creating database(s), declaring node to blockchain or schedule any
    configurable schedule processes.
    :positional arguments:
        rest_conn             REST connection information to send requests against
        config_file           AnyLog INI configuration file
    :optional arguments:
        -h, --help                              show this help message and exit
        -a, --auth,         [AUTH]              comma separated authentication username and password            (default: None)
        -ca, --config-auth  [CONFIG_AUTH]       use authentication found in config file                         (default: False)
        -t, --timeout       [TIMEOUT]           REST timeout (in seconds)                                       (default: 30)
        --anylog            [ANYLOG]            deploy AnyLog docker container                                  (default: False)
        --psql              [PSQL]              deploy postgres docker container if db type is `psql` in config (default: False)
        --grafana           [GRAFANA]           deploy Grafana if `query` in node_type                          (default: False)
        --update-anylog     [UPDATE_ANYLOG]     update docker                                                   (default: False)
        --docker-password   [DOCKER_PASSWORD]   password for docker to download/update AnyLog                   (default: None)
        --docker-only       [DOCKER_ONLY]       If set, code will not continue once docker instance(s) are up   (default: False)
        -e, --exception     [EXCEPTION]         Whether to print exceptions or not                              (default: False)
    :params:
        anylog_conn:anylog_api.AnyLogConnect - connection to AnyLog via REST
        env_configs:dict - configuration parameters from config_file
        env_params:dict - formatted env_configs + parameters from AnyLog dictionary

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('rest_conn', type=str, default='127.0.0.1:2049', help='REST connection information to send requests against')
    parser.add_argument('config_file', type=str, default='$HOME/AnyLog-API/config/single-node.ini', help='AnyLog INI configuration file')

    # REST authentication & timeout
    parser.add_argument('-a', '--auth', type=str, default=None, help='comma separated authentication username and password')
    parser.add_argument('-ca', '--config-auth', type=bool, nargs='?', const=True, default=False, help='use authentication found in config file')
    parser.add_argument('-t', '--timeout', type=int, default=30, help='REST timeout (in seconds')

    # docker deployment
    parser.add_argument('--anylog',          type=bool, nargs='?', const=True, default=False, help='deploy AnyLog docker container')
    parser.add_argument('--psql',            type=bool, nargs='?', const=True, default=False, help='deploy postgres docker container if db type is `psql` in config')
    parser.add_argument('--grafana',         type=bool, nargs='?', const=True, default=False, help='deploy Grafana if `query` in node_type')
    parser.add_argument('--update-anylog',   type=bool, nargs='?', const=True, default=False, help='Update AnyLog build')
    parser.add_argument('--docker-password', type=str, default=None,           help='password for docker to download/update AnyLog')
    parser.add_argument('--docker-only',     type=bool, nargs='?', const=True, default=False, help='If set, code will not continue once docker instances are up')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print exceptions or not')
    args = parser.parse_args()

    auth = None
    status = True

    # validate config_file exists
    config_file = os.path.expandvars(os.path.expanduser(args.config_file))
    if not os.path.isfile(config_file):
        print('Unable to locate configuration file: %s' % config_file)
        exit(1)

    # validate docker is installed
    if bool(pkgutil.find_loader('docker')) is False and (args.anylog is True or args.psql is True or args.grafana is True):
        print('Unable to deploy docker container(s). Missing docker python package.')
        exit(1)

    # extract env_configs
    env_configs, error_msgs = io_configs.read_config(config_file=config_file)
    if error_msgs != []:
        error_msg = 'Failed extract configurations from %s. Errors:' % config_file
        for error in error_msgs:
            error_msg += "\n\t%s" % error
        print(error_msg)
        exit(1)

    # deploy docker container(s)
    if args.psql is True:
        if 'database' not in env_configs:
            env_configs['database'] = {}
        if 'db_user' not in env_configs:
            env_configs['database']['db_user'] = 'anylog@127.0.0.1:demo'
        docker.deploy_postgres(env_params=env_configs['database'], exception=args.exception)

    if args.grafana is True:
        docker.deploy_grafana(exception=args.exception)
    if args.anylog:
        status = docker.deploy_anylog_container(env_configs=env_configs, update_anylog=args.update_anylog,
                                                            docker_password=args.docker_password,
                                                            docker_only=args.docker_only, exception=args.exception)

    if args.config_auth is True and env_configs['authentication']['authentication'] == 'true':
        auth = (env_configs['authentication']['username'], env_configs['authentication']['password'])
    elif args.auth is not None:
        auth = tuple(args.auth.split(','))

    if status is True and env_configs['general']['node_type'] != 'none':
        anylog_conn = anylog_api.AnyLogConnect(conn=args.rest_conn, auth=auth, timeout=args.timeout)
        status = get_cmd.get_status(conn=anylog_conn, exception=args.exception)
   
    # process to execute REST commands
    if args.docker_only is False and env_configs['general']['node_type'] not in ['none', 'rest'] and status is True:
        # deploy generic params
        messages = generic_node.deplog_genric_params(conn=anylog_conn, env_configs=env_configs, exception=args.exception)
        if messages is not []:
            for error in messages:
                print(error)
                exit(1)
        env_params = io_configs.format_configs(env_configs)
        env_params = io_configs.import_config(conn=anylog_conn, env_params=env_params, exception=args.exception)

    elif env_configs['general']['node_type'] == 'rest' and status is True:
        print('AnyLog accessible via REST')



if __name__ == '__main__':
    main()
