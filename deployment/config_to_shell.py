import argparse
import os
import pkgutil
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).rsplit('deployment', 1)[0]
rest_dir = os.path.join(ROOT_PATH, 'rest')
support_dir = os.path.join(ROOT_PATH, 'support')
sys.path.insert(0, rest_dir)
sys.path.insert(0, support_dir)

import print_docker_shell
import io_configs


def print_docker_shell(env_params:dict)->str:
    """
    Given env params, return a docker run call to deploy an AnyLog node
    :args:
        env_params:dict - dict of env params
    :params:
        docker_run_cmd:str - full docker command
    :return:
        docker_run_cmd
    """

    try:
        node_name = env_params['NODE_NAME']
    except:
        node_name = 'new-node'

    docker_run_cmd = "docker run --network host --name new-node --privileged"

    # environment params
    for param in env_params:
        docker_run_cmd += "\n\t-e %s=%s \\" % (param, env_params[param])

    # volume params
    for volume in ['anylog', 'blockchain', 'data', 'local_scripts']:
        docker_run_cmd += "\n\t-v %s-%s:/app/AnyLog-Network/%s \\" % (node_name, volume, volume)

    # image & build information
    try:
        build = env_params['BUILD']
    except:
        build = "predevelop"

    docker_run_cmd += '\n\t-d -it --detach-keys="ctrl-d" oshadmon/anylog:%s' % build

    return docker_run_cmd


def main():
    """
    Given a ini config file, generate a docker run command that can be executed manually
    :positional arguments:
        config_file  AnyLog INI configuration file
    :optional arguments:
        -h, --help   show this help message and exit
    :print:
        generated docker run command
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str, default='$HOME/AnyLog-API/config/single-node.ini', help='AnyLog INI configuration file')
    args = parser.parse_args()

    config_file = os.path.expandvars(os.path.expanduser(args.config_file))
    if not os.path.isfile(config_file):
        print('Unable to locate configuration file: %s' % config_file)
        exit(1)

    env_configs, error_msgs = io_configs.read_config(config_file=config_file)
    if error_msgs != []:
        error_msg = 'Failed extract configurations from %s. Errors:' % config_file
        for error in error_msgs:
            error_msg += "\n\t%s" % error
        print(error_msg)
        exit(1)

    configs_to_docker = io_configs.format_configs(env_configs)
    print(print_docker_shell(configs_to_docker))


if __name__ == '__main__':
    main()