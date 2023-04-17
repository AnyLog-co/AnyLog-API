import argparse
import os

import anylog_connector
import blockchain
import generic_get
import generic_post
import deployment_support


ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]


def main():
    """
    :positional arguments:
        rest_conn             REST connection information (example: {user}:{password}@
        config_file           Configuration file to be utilized
        license_key           AnyLog License Key

    :optional arguments:
        -h, --help                      show this help message and exit
        --timeout       TIMEOUT         REST timeout (default: 30)
        -e,--exception  [EXCEPTION]     Whether to print errors (default: False)
    :params:
        config_file:str - configuration file
        conn:str - REST connection IP and Port
        auth:tuple - REST authentication
        anylog_conn:anylog_connector.AnyLogConnector - Connection to AnyLog via REST
        configuration:dict - deployment configurations (both file and AnyLog dictionary)
    """
    config_file=os.path.join(ROOT_DIR, 'configurations', 'master_configs.env')
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn', type=deployment_support.validate_conn_pattern, default='127.0.0.1:2049', help='REST connection information')
    parser.add_argument('config_file', type=str, default=config_file, help='Configuration file to be utilized')
    parser.add_argument('license_key', type=str, default=None, help='AnyLog License Key')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = parser.parse_args()

    conn, auth = deployment_support.anylog_connection(rest_conn=args.rest_conn)
    anylog_conn = anylog_connector.AnyLogConnector(conn=conn, auth=auth, timeout=args.timeout, exception=args.exception)

    if generic_get.get_status(anylog_conn=anylog_conn, json_format=True) is False:
        print(f"Failed to connect to AnyLog via {conn}. Cannot Continue")
        exit(1)

    if generic_post.set_license_key(anylog_conn=anylog_conn, license_key=args.license_key) is False:
        print(f"Failed to utilize given license to enable AnyLog {conn}. Cannot continue")
        exit(1)

    configuration = deployment_support.prepare_dictionary(anylog_conn=anylog_conn, config_file=args.config_file,
                                                          exception=args.exception)

    if len(configuration) == 0 or configuration is None:
        print(f"Failed to get configurations against file {args.config_file} and connection {conn}. Cannot continue")
        exit(1)

    if configuration['node_type'] not in ['rest', 'none']:
            if deployment_support.check_synchronizer(anylog_conn=anylog_conn) is False:
                if blockchain.run_synchronizer(anylog_conn=anylog_conn, source=configuration['blockchain_source'],
                                               time=configuration['sync_time'],
                                               dest=configuration ['blockchain_destination'],
                                               connection=configuration['ledger_conn'], view_help=False) is False:
                    print(f"Failed to declare blockchain sync against {conn}")

    if configuration['node_type'] in ['master', 'ledger', 'standalone', 'standalone-publisher']:
        pass
    if configuration['node_type'] in ['operator', 'standalone']:
        pass
    if configuration['node_type'] in ['publisher', 'standalone-publisher']:
        pass
    if configuration['node_type'] in ['query']:
        pass

    print(generic_get.get_processes(anylog_conn=anylog_conn, json_format=False, view_help=False))


if __name__ == '__main__':
    main()