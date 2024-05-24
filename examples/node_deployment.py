import argparse
import ast

import __support__ as support

import anylog_api.anylog_connector as anylog_connector
import anylog_api.generic.get as generic_get
import anylog_api.generic.post as generic_post
import anylog_api.generic.logs as logs_cmds
import anylog_api.generic.networking as generic_networking
from anylog_api.__support__ import get_generic_params

import anylog_api.blockchain.cmds as blockchain_cmds
import anylog_api.blockchain.policy as blockchain_policy

def __validate_connection(conn:anylog_connector.AnyLogConnector, exception:bool=False):
    """
    Validate whether the node is running - if fails code
    """
    # validate node is running
    if generic_get.get_status(conn=conn, destination=None, view_help=False, return_cmd=False,
                              exception=exception) is False:
        print(f"Failed to communicated with {conn.conn}. cannot continue...")
        exit(1)


def __set_params(conn:anylog_connector.AnyLogConnector, config_files:str, exception:bool=False):
        """
        Set node configurations
        :process:
            1. get default configs
            2. read config file
            3. merge comfigs
            4. if node_type is missing goto node_state
        """
        # get preset / default params
        generic_params = get_generic_params(conn=conn, exception=exception)
        file_configs = {}

        # get configs from file
        if config_files is not None:
            file_configs = support.read_configs(config_file=config_files, exception=exception)
        # merge configs
        if file_configs:
            for config in file_configs:
                if file_configs[config]:
                    generic_params[config.lower()] = file_configs[config]
        err_msg = ""
        for config in ['node_type', 'node_name', 'company_name', 'ledger_conn']:
            if config not in generic_params or generic_params[config] == "":
                if err_msg == "":
                    err_msg = f"Missing key config param(s). Param List: {config}"
                else:
                    err_msg += f", {config}"
        if err_msg != "":
            print(err_msg)
            __node_state(conn=conn, exception=exception)
        else:
            generic_post.set_params(conn=conn, params=generic_params, destination=None, view_help=False,
                                    exception=exception)
        return generic_params


def __configure_directories(conn:anylog_connector.AnyLogConnector, anylog_path:str, exception:bool=False):
    """
    Configure directories in node
    :process:
        1. st anylog home path
        2. create work directories
    """
    generic_post.set_path(conn=conn, path=anylog_path, destination=None, view_help=False, returnn_cmd=False,
                          exception=exception)

    generic_post.create_work_dirs(conn=conn, destination=None, view_help=False, return_cmd=False, exception=exception)


def __declare_node_policy(conn:anylog_connector.AnyLogConnector, node_configs:dict, cluster_id:str=None,
                          exception:bool=False):
    node_type = node_configs['node_type']
    node_name = node_configs['node_name']
    company = node_configs['company_name']
    external_ip = None
    local_ip = None
    anylog_server_port = None
    anylog_rest_port = None
    anylog_broker_port = None
    tcp_bind = False
    rest_bind = False
    broker_bind = False
    if 'external_ip' in node_configs:
        external_ip = node_configs['external_ip']
    if 'ip' in node_configs:
        local_ip = node_configs['ip']
    if 'anylog_server_port' in node_configs:
        anylog_server_port = node_configs['anylog_server_port']
    if 'anylog_rest_port' in node_configs:
        anylog_rest_port = node_configs['anylog_rest_port']
    if 'anylog_broker_port' in node_configs:
        anylog_broker_port = node_configs['anylog_broker_port']
    if cluster_id is None and 'cluster_id' in node_configs:
        cluster_id = node_configs['cluster_id']
    if 'tcp_bind' in node_configs:
        tcp_bind = node_configs['tcp_bind']
    if 'rest_bind' in node_configs:
        rest_bind = node_configs['rest_bind']
    if 'broker_bind' in node_configs:
        broker_bind = node_configs['broker_bind']



    is_blockckchain = blockchain_cmds.get_policy(conn=conn, policy_type=node_type,
                                                 where_condition=f"name={node_name} and company={company}")
    if is_blockckchain is None:
        policy = blockchain_policy.node_policy(conn=conn, node_type=node_type, name=node_name, company=company,
                                               external_ip=external_ip, local_ip=local_ip,
                                               anylog_server_port=anylog_server_port, anylog_rest_port=anylog_rest_port,
                                               anylog_broker_port=anylog_broker_port, tcp_bind=tcp_bind,
                                               rest_bind=rest_bind, broker_bind=broker_bind,  cluster_id=cluster_id,
                                               set_geolocation=True, policy_id=None, other_params={}, scripts=[],
                                               exception=exception)

        blockchain_cmds.prepare_policy(conn=conn, policy=policy, destination=None, view_help=False, return_cmd=False,
                                       exception=exception)




def __node_state(conn:anylog_connector.AnyLogConnector, exception:bool=False):
    """
    Check the state of the node
    :checks:
        1. test node
        2. test network
        3. show processes
    """
    print("Test Node Networking")
    output = generic_networking.test_node(conn=conn, destination=None, view_help=False, return_cmd=False,
                                          exception=exception)
    print(output)

    print("Test Network Status")
    output = generic_networking.test_network(conn=conn, destination=None, view_help=False, return_cmd=False,
                                             exception=exception)
    print(output)

    print("View Running Process")
    output = logs_cmds.get_processes(conn=conn, json_format=False, destination=None, view_help=False,
                                     return_cmd=False, exception=exception)
    print(output)
    exit(1)




def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("conn", type=support.check_conn, default='127.0.0.1:32549', help='REST connection information')
    parse.add_argument('--configs', type=support.check_configs, default=None, help='dotenv configuration file(s)')
    parse.add_argument('--timeout', type=float, default=30, help='REST timeout')
    parse.add_argument('--exception', type=bool, const=True, nargs='?', default=False, help='Print exception')
    args = parse.parse_args()

    conn, auth = next(iter(args.conn.items()))
    anylog_conn = anylog_connector.AnyLogConnector(conn, auth=auth, timeout=args.timeout)

    # prepare node
    __validate_connection(conn=anylog_conn, exception=args.exception)
    node_params = __set_params(conn=anylog_conn, config_files=args.configs, exception=args.exception)
    __configure_directories(conn=anylog_conn, anylog_path=node_params['anylog_path'], exception=args.exception)

    # blockchain seed
    if node_params['node_type'] not in ['generic', 'master']:
        if not blockchain_cmds.execute_seed(conn=anylog_conn, ledger_conn=node_params['ledger_conn'], destination="",
                                            view_help=False, return_cmd=False, exception=args.exception):
            print("Failed to execute blockchain seed  command")

    __declare_node_policy(conn=anylog_conn, node_configs=node_params, cluster_id=None, exception=args.exception)

    __node_state(conn=anylog_conn, exception=args.exception)


if __name__ == '__main__':
    main()