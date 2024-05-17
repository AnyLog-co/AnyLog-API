"""
Process
    1. read configs file(s)
    2. check status
    3. set anylog path
    4. declare config policy
    5. declare node policy
    6. set license
"""
import argparse
import __support__  as support
import anylog_api.anylog_connector  as anylog_connector
import anylog_api.anylog_connector_support as anylog_connector_support
import anylog_api.generic.get as generic_get
import anylog_api.generic.post as generic_post


def main():
    """
    The following is intended to replicate the default deployment done with the default deployment script(s)
     :url:
        https://github.com/AnyLog-co/deployment-scripts
    :positional arguments:
        conn                  REST connection information
        configs               dotenv configuration file(s)
    :options:
      -h, --help                    show this help message and exit
      --timeout      TIMEOUT        REST timeout
      --exception    [EXCEPTION]    Print exception
    :params:
         conn:str - REST IP:Port
         auth:tuple - authentication for REST
         full_configs:dict - configurations both file + built in
         is_edgelake:bool - whether you're running EdgeLake or AnyLog
    """
    parse = argparse.ArgumentParser()
    parse.add_argument("conn", type=support.check_conn, default='127.0.0.1:32549', help='REST connection information')
    parse.add_argument('configs', type=support.check_configs, default=None, help='dotenv configuration file(s)')
    parse.add_argument('--timeout', type=float, default=30, help='REST timeout')
    parse.add_argument('--exception', type=bool, const=True, nargs='?', default=False, help='Print exception')
    args = parse.parse_args()

    conn, auth = next(iter(args.conn.items()))
    anylog_conn = anylog_connector.AnyLogConnector(conn)

    # check status
    if generic_get.get_status(conn=anylog_conn, view_help=False, exception=args.exception) is True:
        print("Node is Running")
    else:
        print(f"Failed to communicate with node against {anylog_conn.conn}. Cannot continue...")
        exit(1)

    # set configurations
    node_configs = generic_get.get_dictionary(conn=anylog_conn, json_format=True, destination=None, view_help=False, exception=args.exception)
    full_configs = {}
    for file_path in args.configs:
        full_configs.update(support.read_configs(file_path, exception=args.exception))
    for key in node_configs:
        if key not in full_configs:
            full_configs[key] = node_configs[key]

    # check if EdgeLake
    is_edgelake = anylog_connector_support.is_edgelake(conn=anylog_conn, exception=args.exception)

    # set set-configs
    generic_post.set_debug(conn=anylog_conn, state='off', destination=None, view_help=False, exception=args.exception)
    generic_post.set_echo_queue(conn=anylog_conn, state='on', destination=None, view_help=False, exception=args.exception)
    if is_edgelake is False:
        generic_post.set_authentication(conn=anylog_conn, state='on', destination=None, view_help=False, exception=args.exception)

    # set params
    generic_post.set_params(conn=anylog_conn, params=full_configs, destination=None, view_help=False, exception=args.exception)
    if 'node_name' in full_configs:
        generic_post.set_node_name(conn=anylog_conn, node_name=full_configs['node_name'], destination=None, view_help=False, exception=args.exception)
    if 'disable_cli' in full_configs and full_configs['disable_cli'] in [True, 'true', 'True']:
        generic_post.disable_cli(conn=conn, destination=None, view_help=False, exception=args.exception)

    # directories
    if 'anylog_path' in full_configs:
        generic_post.set_path(conn=anylog_conn, path=full_configs['anylog_path'], destination=None, view_help=False,
                              exception=args.exception)
    if 'edgelake_path' in full_configs:
        generic_post.set_path(conn=anylog_conn, path=full_configs['edgelake_path'], destination=None, view_help=False,
                              exception=args.exception)
    generic_post.create_work_dirs(conn=anylog_conn, destination=None, view_help=False, exception=args.exception)


if __name__ == '__main__':
    main()