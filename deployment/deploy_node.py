import argparse
import os

import anylog_connector
import generic_get
import generic_post
import deployment_support


ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]


def main():
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

    count = 0
    status = generic_get.check_license(anylog_conn=anylog_conn)
    while status is False:
        if generic_post.set_license_key(anylog_conn=anylog_conn, license_key=args.license_key) is False:
            print(f"Failed to utilize given license to enable AnyLog {conn}. Cannot continue")
            exit(1)
        status = generic_get.check_license(anylog_conn=anylog_conn)
        if count > 0:
            print(f"Issue with license against {conn}. Cannot continue")
            exit(1)
        else:
            count += 1



if __name__ == '__main__':
    main()