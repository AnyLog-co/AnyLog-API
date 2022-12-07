import argparse
import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

import generic_get_calls

import declare_dbms
import run_scheduler
import config_node
import declare_policies


def main():
    """
    The following deploys an AnyLog instance using REST. This deployment process requires the node to already be up
    running with at least TCP and REST communication.
    :process:
        1. connect to AnyLog + get params
        2. connect to database
        3. run scheduler / blockchain sync
        4. declare policies
        5. set partitions (operator only)
        6. buffer & streaming
        7. publisher / operator `run` process
    :positional arguments:
        rest_conn             REST connection information
        config_file           Configuration file to be utilized
    :optional arguments:
        -h, --help                          show this help message and exit
        --auth              AUTH            Authentication information (comma separated) [ex. username,password] (default: None)
        --timeout           TIMEOUT         REST timeout (default: 30)
        -e, --exception     [EXCEPTION]     Whether to print errors (default: False)
    :params:
        config_file_path:str - full path of config_file
        anylog_conn:AnyLogConnection - connection to AnyLog node
        configs:str - configuration file
    """
    config_file=os.path.join(ROOT_DIR, 'deployments/sample_configs.env')
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn', type=str, default='127.0.0.1:2049', help='REST connection information')
    parser.add_argument('config_file', type=str, default=config_file, help='Configuration file to be utilized')
    parser.add_argument('--auth', type=str, default=None, help='Authentication information (comma separated) [ex. username,password]')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = parser.parse_args()

    # set configs
    config_file_path = os.path.expanduser(os.path.expandvars(args.config_file))
    if not os.path.isfile(config_file_path):
        print(f'Failed to locate file {args.config_file}')
        exit(1)
    anylog_conn, configs = config_node.config_node(rest_conn=args.rest_conn, config_file=config_file_path,
                                                   auth=args.auth, timeout=args.timeout, exception=args.exception)

    # validate connection
    if generic_get_calls.get_status(anylog_conn=anylog_conn, exception=args.exception) is False:
        print(f'Failed to connect to AnyLog instance against {args.rest_conn}')
        exit(1)

    # connect databases
    declare_dbms.declare_database(anylog_conn=anylog_conn, node_type=configs['NODE_TYPE'], enable_nosql=False,
                                  db_name=configs['DEFAULT_DBMS'], db_type=configs['DB_TYPE'], host=configs['DB_IP'],
                                  port=configs['DB_PORT'], user=configs['DB_USER'], password=configs['DB_PASSWD'],
                                  system_query=configs['SYSTEM_QUERY'], memory=configs['MEMORY'],
                                  exception=args.exception)
    if configs['NOSQL_ENABLE'] is True:
        declare_dbms.declare_database(anylog_conn=anylog_conn, node_type=configs['NODE_TYPE'], enable_nosql=True,
                                      db_name=configs['DEFAULT_DBMS'], db_type=configs['NOSQL_TYPE'],
                                      host=configs['NOSQL_IP'], port=configs['NOSQL_PORT'], user=configs['NOSQL_USER'],
                                      password=configs['NOSQL_PASSWD'], exception=args.exception)

    # run scheduler
    run_scheduler.run_scheduler(anylog_conn=anylog_conn, blockchain_source=configs['BLOCKCHAIN_SOURCE'],
                                blockchain_destination=configs['BLOCKCHAIN_DESTINATION'], sync_time=configs['SYNC_TIME'],
                                ledger_conn=configs['LEDGER_CONN'], exception=args.exception)

    # declare policy
    declare_policies.declare_policies(anylog_conn=anylog_conn, node_type=configs['NODE_TYPE'], name=configs['NODE_NAME'],
                                      company=configs['COMPANY_NAME'].replace('"', ''), hostname=configs['HOSTNAME'],
                                      external_ip=configs['EXTERNAL_IP'], local_ip=configs['IP'],
                                      anylog_server_port=configs['ANYLOG_SERVER_PORT'],
                                      anylog_rest_port=configs['ANYLOG_REST_PORT'], db_name=configs['DEFAULT_DBMS'],
                                      cluster_name=configs['CLUSTER_NAME'], member=configs['MEMBER'],
                                      location=configs['LOCATION'], country=configs['COUNTRY'],
                                      state=configs['STATE'], city=configs['CITY'], exception=args.exception)

    # set partitions (operator only)

    # buffer & streaming

    # publisher / operator `run` command

    # run mqtt client



if __name__ == '__main__':
    main()