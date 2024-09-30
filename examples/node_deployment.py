import argparse
import os

import __support__ as support

import anylog_api.anylog_connector as anylog_connector
import anylog_api.generic.get as generic_get
import anylog_api.generic.post as generic_post
import anylog_api.blockchain.cmds as blockchain_cmds


def __validate_connection(conn:anylog_connector.AnyLogConnector, exception:bool=False):
    """
    Validate whether the node is running - if fails code
    """
    # validate node is running
    if generic_get.get_status(conn=conn, destination=None, view_help=False, return_cmd=False,
                              exception=exception) is False:
        print(f"Failed to communicated with {conn.conn}. cannot continue...")
        exit(1)


def __set_dictionary(conn:anylog_connector.AnyLogConnector, config_files:str, exception:bool=False):
    """
    Set node configurations
    :process:
        1. get default configs
        2. read config file
        3. merge comfigs
        4. if node_type is missing goto node_state
    """
    # get preset / default params
    generic_params = generic_get.get_dictionary(conn=conn, json_format=True, destination="", view_help=False,
                                                return_cmd=False, exception=exception)
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



def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("conn", type=support.check_conn, default='127.0.0.1:32549', help='REST connection information')
    parse.add_argument('--configs', type=support.check_configs, default=None, help='dotenv configuration file(s)')
    parse.add_argument('--timeout', type=float, default=30, help='REST timeout')
    parse.add_argument('--edgelake',  type=bool, const=True, nargs='?', default=False, help='Connect to EdgeLake instance')
    parse.add_argument('--exception', type=bool, const=True, nargs='?', default=False, help='Print exception')
    args = parse.parse_args()
    args.configs = os.path.expanduser(os.path.expandvars(args.configs[0]))

    conn, auth = next(iter(args.conn.items()))
    anylog_conn = anylog_connector.AnyLogConnector(conn, auth=auth, timeout=args.timeout)

    # set license if using AnyLog
    if args.edgelake is False:
        params = support.read_configs(config_file=args.configs, exception=args.exception)
        if 'LICENSE_KEY' in params:
            generic_post.set_license_key(conn=anylog_conn, license_key=params['LICENSE_KEY'], view_help=False,
                                         return_cmd=False, exception=args.exception)
    # validate node
    node_status = generic_get.get_status(conn=anylog_conn, view_help=False, return_cmd=False, exception=args.exception)
    if node_status is False:
        print(f"Failed to communicate with node against {conn}. Cannot continue...")
        exit(1)

    # set node params to be used
    node_params = __set_dictionary(conn=anylog_conn, config_files=args.configs, exception=args.exception)
    if not generic_post.set_path(conn=anylog_conn, path=node_params['anylog_path'], exception=args.exception):
        print(f"Failed to set root_path to {node_params['anylog_path']}")
    if not generic_post.set_node_name(conn=anylog_conn, node_name=node_params['node_name'], exception=args.exception):
        print(f"Failed to set node name to {node_params['node_name']}")
    if not generic_post.create_work_dirs(conn=anylog_conn, exception=args.exception):
        print(f"Failed to create work directories")
    generic_post.set_params(conn=anylog_conn, params={'local_scripts': node_params['local_scripts'],
                                                      'test_dir': node_params['test_dir']}, exception=args.exception)

    if node_params['node_type'] != 'generic':
        pass

    # view processes
    print(generic_get.get_processes(conn=anylog_conn, json_format=False, exception=args.exception))

    # # prepare node
    # __validate_connection(conn=anylog_conn, exception=args.exception)
    #
    # __configure_directories(conn=anylog_conn, anylog_path=node_params['anylog_path'], exception=args.exception)
    #
    # # blockchain seed
    # status, cmd = blockchain_cmds.execute_seed(conn=anylog_conn, ledger_conn=node_params['ledger_conn'], destination="",
    #                                            view_help=False, return_cmd=False,  exception=args.exception)
    # if status is False:
    #     print(f"Failed to execute blockchain seed from {node_params['ledger_conn']}")
    #
    # # check policy
    #
    #
    # # __node_state(conn=anylog_conn, exception=args.exception)
    #

if __name__ == '__main__':
    main()