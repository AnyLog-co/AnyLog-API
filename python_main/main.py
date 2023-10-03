import argparse
import os.path

from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.generic_get_calls import get_status, get_dictionary
from anylog_api_py.generic_post_calls import set_node_name

from anylog_api_py.rest_support import check_conn_format
from anylog_api_py.__support__ import dictionary_merge
from node_configs import get_configs


from file_io import read_configs
from generic import declare_directories

ROOT_DIR = os.path.expanduser(os.path.expandvars(__file__)).split('python_main')[0]

def __convert_conn(conn:str)->(str, tuple):
    """
    Configure connection information separate IP:PORT + auth
    :args:
        conn:str - REST coectio
    :params:
        auth:tuple - REST autheentication
    :return:
        conn, auth
    """
    auth = ()
    if '@' in conn:
        auth, conn = conn.split('@')
        auth = tuple(auth.split(':'))
    return conn, auth


def main():
    """
    :params:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('conn', type=check_conn_format, default='127.0.0.1:32549', help='REST connection information')
    parser.add_argument('config_file', type=str, default=None, help='Configuration file')
    parser.add_argument('--rest-timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('--exception', type=bool, nargs='?', const=True, default=False, help='Print Exceptions')
    args = parser.parse_args()

    conn, auth = __convert_conn(conn=args.conn)
    anylog_conn = AnyLogConnector(conn=conn, auth=auth, timeout=args.rest_timeout)
    if get_status(anylog_conn=anylog_conn, remote_destination=None, view_help=False, exception=args.exception) is False:
        print(f"Failed to connect against: {conn}. Cannot continue...")
        exit(1)

    node_configs = get_configs(anylog_conn=anylog_conn, config_file=args.config_file, exception=args.exception)

    """
    set default params
        1. create directories 
        2. set node name 
    """
    declare_directories(anylog_conn=anylog_conn, anylog_path=ROOT_DIR, exception=args.exception)
    node_name = 'anylog-node'
    if 'node_name' in node_configs:
        node_name = node_configs['node_name']
    if not set_node_name(anylog_conn=anylog_conn, node_name=node_name, destination=None, view_help=False, exception=args.exception):
        print(f"Failed to set node name to {node_name}. cannot continue...")
        exit(1)

    """
    users may want to rerun node configs as creating directories changes / may change some of the physical node 
    configurations
    """
    node_configs = get_configs(anylog_conn=anylog_conn, config_file=args.config_file, exception=args.exception)




if __name__ == '__main__':
    main()

