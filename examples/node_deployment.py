import argparse
import __support__ as support

import anylog_api.anylog_connector as anylog_connector
import anylog_api.generic.get as generic_get
import anylog_api.generic.post as generic_post
import anylog_api.generic.logs as logs_cmds
import anylog_api.generic.networking as generic_networking
from anylog_api.__support__ import get_generic_params


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

    if node_params['node_type'] == 'generic':
        pass

    __node_state(conn=anylog_conn, exception=args.exception)






if __name__ == '__main__':
    main()