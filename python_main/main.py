import argparse

from generic_node_config import setup_configurations
from file_io import check_file, read_configs

from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.generic_get_calls import get_status, get_license, get_processes
from anylog_api_py.generic_post_calls import set_license_key, add_dict_params
from anylog_api_py.rest_support import check_conn_format, extract_conn_information


def main():
    """
    Process
        1. validate connection
        2. set license key
        3. set env params (config_file)
        4. based on env params redeclare network
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('conn', type=check_conn_format, default='127.0.0.1:32548', help='REST connection information (format ip:port or user:passwd@ip:port)')
    parser.add_argument("config_file", type=check_file, default=None, help='AnyLog configuration file')
    parser.add_argument('license_key', type=str, default=None, help='AnyLog license key')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='whether to print exceptions')
    args = parser.parse_args()

    conn, auth = extract_conn_information(conn_ip_port=args.conn)
    anylog_conn = AnyLogConnector(conn=conn, auth=auth, timeout=args.timeout)

    if get_status(anylog_conn=anylog_conn, remote_destination=None, view_help=False, exception=args.exception) is False:
        print(f"Failed to connect to AnyLog against {conn} with credentials {auth}. Cannot continue...")
        exit(1)

    if set_license_key(anylog_conn=anylog_conn, license_key=args.license_key, remote_destination=None, view_help=False,
                       exception=args.exception) is False:
        print(f"Failed to set license key, cannot continue...")
        exit(1)

    node_configs = setup_configurations(anylog_conn=anylog_conn, config_file=args.config_file, exception=args.exception)
    print(node_configs)

    print(get_license(anylog_conn=anylog_conn, remote_destination=None, view_help=False, exception=args.exception))
    print(get_processes(anylog_conn=anylog_conn, json_format=False, remote_destination=None, view_help=False, exception=args.exception))


if __name__ == '__main__':
    main()

