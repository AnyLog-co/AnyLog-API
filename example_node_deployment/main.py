import argparse
import os

import anylog_api.anylog_connector as anylog_connector
import anylog_api.blockchain.cmds as blockchain_cmds
import anylog_api.generic.get as generic_get
import anylog_api.generic.post as generic_post
import anylog_api.generic.scheduler as scheduler

import example_node_deployment.__support__ as support
import example_node_deployment.__support_files__ as support_file
from example_node_deployment.database import connect_dbms
import example_node_deployment.create_policy as create_policy
from examples.__support__ import  check_conn


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("conn", type=check_conn, default='127.0.0.1:32549', help='REST connection information')
    parse.add_argument('--configs', type=support_file.check_configs, default=None, help='dotenv configuration file(s)')
    parse.add_argument('--timeout', type=float, default=30, help='REST timeout')
    parse.add_argument('--edgelake',  type=bool, const=True, nargs='?', default=False, help='Connect to EdgeLake instance')
    parse.add_argument('--exception', type=bool, const=True, nargs='?', default=False, help='Print exception')
    parse.add_argument('--license-key', type=str, default=None, help='License key fo AnyLog if not part of configs')
    args = parse.parse_args()
    args.configs = os.path.expanduser(os.path.expandvars(args.configs[0]))

    conn, auth = next(iter(args.conn.items()))
    anylog_conn = anylog_connector.AnyLogConnector(conn, auth=auth, timeout=args.timeout)

    # set params from config file
    params = support_file.read_configs(config_file=args.configs, exception=args.exception)

    # set license if using AnyLog
    status = True
    if args.edgelake is False and args.license_key is not None:
        status = generic_post.set_license_key(conn=anylog_conn, license_key=args.license_key, view_help=False,
                                     return_cmd=False, exception=args.exception)
    elif args.edgelake is False and 'license_key' in params:
        status = generic_post.set_license_key(conn=anylog_conn, license_key=params['license_key'], view_help=False,
                                              return_cmd=False, exception=args.exception)
    elif args.edgelake is False:
        print(f"Failed to set license key for AnyLog, cannot continue...")
        exit(1)
    if  args.edgelake is False:
        if status is True:
            print("License Key\n" + generic_get.get_license_key(conn=anylog_conn, view_help=False, return_cmd=False, exception=args.exception))


    # validate node
    node_status = generic_get.get_status(conn=anylog_conn, view_help=False, return_cmd=False, exception=args.exception)
    if node_status is False:
        print(f"Failed to communicate with node against {conn}. Cannot continue...")
        exit(1)

    # set node params to be used
    node_params = support.set_dictionary(conn=anylog_conn, config_files=args.configs, exception=args.exception)
    if not generic_post.set_path(conn=anylog_conn, path=node_params['anylog_path'], exception=args.exception):
        print(f"Failed to set root_path to {node_params['anylog_path']}")
    if not generic_post.set_node_name(conn=anylog_conn, node_name=node_params['node_name'], exception=args.exception):
        print(f"Failed to set node name to {node_params['node_name']}")
    if not generic_post.create_work_dirs(conn=anylog_conn, exception=args.exception):
        print(f"Failed to create work directories")

    if node_params['node_type'] != 'publisher' and args.edgelake is True:
        print(f"Publisher node not supported with EdgeLake.")
        is_operator = None
        error = ""
        input_cmd = "Would you like to run an operator node instead [y/N]? "
        while is_operator not in ['y', 'n']:
            is_operator = input(error + input_cmd).lower()
            if is_operator not in ['y', 'n']:
                error = f"Invalid value {is_operator}, please try again... "
            elif is_operator is 'y':
                node_params['node_type'] = 'operator'

    generic_post.set_params(conn=anylog_conn, params={'local_scripts': node_params['local_scripts'],
                                                      'test_dir': node_params['test_dir']}, exception=args.exception)

    # schedule 1
    scheduler.run_scheduler(conn=conn, schedule_id=1, exception=args.exception)

    # create database / tables
    connect_dbms(conn=conn, params=params, destination=None, view_help=False, return_cmd=False,
                 exception=args.exception)

    # blockchain seed
    blockchain_cmds.execute_seed(conn=conn, ledger_conn=params['ledger_conn'], destination="",
                                 view_help=False, return_cmd=False, exception=args.exception)

    # create policy
    cluster_id = None
    if params['node_type'] == 'operator':
        if 'cluster_name' not in params:
            params['cluster_name'] = 'new-cluster'
        cluster_id = create_policy.create_cluster(conn=conn, cluster_name=params['cluster_name'],
                                                  owner=params['company_name'], ledger_conn=params['ledger_conn'],
                                                  db_name=None, table=None, parent=None, destination="",
                                                  view_help=False, return_cmd=False, exception=args.exception)
    policy_id = create_policy.generate_policy(conn=conn, params=params, destination=None, view_help=False,
                                              return_cmd=False, exception=False)

    if params['node_type'] == 'operator':
        pass

    # view processes
    print(generic_get.get_processes(conn=anylog_conn, json_format=False, exception=args.exception))


if __name__ == '__main__':
    main()