import argparse
import ast
import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from anylog_connection import AnyLogConnection
import blockchain_calls as blockchain_calls
import database_calls as database_calls
import generic_get_calls as generic_get_calls
import generic_post_calls as generic_post_calls
import support

def standalone():
    """
    The following script deploys a standalone (master + operator on a single node) AnyLog instance.
    The only requirement is having REST + TCP already running on the node.
    :params:
        status:bool
        config_file:str - extract full path of config file
        yaml_config:dict - configs in config_file
        auth:tuple - authentication
        anylog_conn:anylog_connection.AnyLogConnection - connection to AnyLog
        anylog_dictionary:dict - content in AnyLog dictionary
        full_configs:dict - merged config dictionaries
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn', type=str, default='127.0.0.1:2049', help='REST connection information')
    parser.add_argument('config_file', type=str, default=os.path.join(ROOT_DIR, 'deployments/sample_configs.yaml'),  help='Sample configurations file')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('--auth', type=str, default=None, help='Authentication information (comma separated) [ex. username,password]')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = parser.parse_args()

    # Extract configurations from YAML file
    config_file = os.path.expanduser(os.path.expandvars(args.config_file))
    if not os.path.isfile(config_file):
        print(f'Unable to locate configuration file {config_file}')
        exit(1)
    yaml_config = support.read_configs(config_file=config_file, exception=args.exception)

    # Set authentication
    auth = None
    if args.auth is not None:
        auth = tuple(args.auth.split(','))

    # connect to AnyLog node
    anylog_conn = AnyLogConnection(conn=args.rest_conn, auth=auth, timeout=args.timeout)
    if not generic_get_calls.validate_status(anylog_conn=anylog_conn, exception=args.exception):
        print(f'Failed to validate connection to: {args.rest_conn}')
        exit(1)

    anylog_dictionary = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, exception=args.exception)
    anylog_dictionary['hostname'] = generic_get_calls.get_hostname(anylog_conn=anylog_conn, exception=args.exception)
    full_configs = support.dictionary_merge(yaml_config=yaml_config, anylog_dictionary=anylog_dictionary)
    if full_configs == {}:
        print('Failed to get configurations. Cannot continue')
        exit(1)

    # connect to broker if set
    if 'anylog_broker_port' in full_configs:
        if not generic_post_calls.network_connection(anylog_conn=anylog_conn, connection_type='message broker',
                                                     external_ip=full_configs['external_ip'],
                                                     local_ip=full_configs['ip'],
                                                     port=full_configs['anylog_broker_port'], exception=args.exception):
            print(f"Failed to connect to AnyLog broker against port: {full_configs['anylog_broker_port']}")

    # connect database(s) & tables
    if full_configs['node_type'] in ['master', 'standalone', 'standalone-publisher']:
        if full_configs['db_type'] != 'sqlite':
            status = database_calls.connect_db(anylog_conn=anylog_conn, db_type=full_configs['db_type'],
                                               db_name='blockchain', host=full_configs['db_ip'],
                                               port=full_configs['db_port'], user=full_configs['db_user'],
                                               passwd=full_configs['db_passwd'], exception=args.exception)

        else:
            status = database_calls.connect_db(anylog_conn=anylog_conn, db_type=full_configs['db_type'],
                                               db_name='blockchain', exception=args.exception)
        if status is False:
            print('Failed to create blockchain logical database')


        if not database_calls.create_table(anylog_conn=anylog_conn, db_name='blockchain', table_name='ledger',
                                           exception=args.exception):
            print('Failed to create ledger table in blockchain database')

    if full_configs['node_type'] in ['operator', 'standalone']:
        if full_configs['db_type'] != 'sqlite':
            status = database_calls.connect_db(anylog_conn=anylog_conn, db_type=full_configs['db_type'],
                                               db_name=full_configs['default_dbms'], host=full_configs['db_ip'],
                                               port=full_configs['db_port'], user=full_configs['db_user'],
                                               passwd=full_configs['db_passwd'], exception=args.exception)
        else:
            status = database_calls.connect_db(anylog_conn=anylog_conn, db_type=full_configs['db_type'],
                                               db_name=full_configs['default_dbms'], exception=args.exception)
        if status is False:
            print(f"Failed to create {full_configs['default_dbms']} logical database")

    if full_configs['node_type'] in ['operator', 'standalone', 'publisher', 'standalone-publisher']:
        if full_configs['db_type'] != 'sqlite':
            status = database_calls.connect_db(anylog_conn=anylog_conn, db_type=full_configs['db_type'],
                                               db_name='almgm', host=full_configs['db_ip'],
                                               port=full_configs['db_port'], user=full_configs['db_user'],
                                               passwd=full_configs['db_passwd'], exception=args.exception)
        else:
            status = database_calls.connect_db(anylog_conn=anylog_conn, db_type=full_configs['db_type'],
                                               db_name='almgm', exception=args.exception)
        if status is False:
            print(f"Failed to create almgm logical database")

        if not database_calls.create_table(anylog_conn=anylog_conn, db_name='almgm', table_name='tsd_info',
                                           exception=args.exception):
            print('Failed to create tsd_info table in almgm database')

    if not database_calls.connect_db(anylog_conn=anylog_conn, db_type='sqlite', db_name='system_query',
                              memory=full_configs['memory'], exception=args.exception):
        print('Failed to create system_query logical database')


    # run scheduler 1
    if not generic_post_calls.schedule_task(anylog_conn=anylog_conn, name=1, exception=args.exception):
        print('Failed to run scheduler 1 process')

    """
    blockchain process
    1. check if policy exists 
    2. if DNE create policy & POST policy
    """
    # run blockchain sync
    blockchain_calls.blockchain_sync(anylog_conn=anylog_conn, blockchain_source=full_configs['blockchain_source'],
                                     blockchain_destination=full_configs['blockchain_destination'],
                                     sync_time=full_configs['sync_time'], ledger_conn=full_configs['ledger_conn'],
                                     exception=args.exception)


    # master
    if not blockchain_calls.check_policy_exists(anylog_conn=anylog_conn, policy_type='master',
                                                name=full_configs['node_name'], company=full_configs['company_name'],
                                                local_ip=full_configs['ip'],
                                                anylog_server_port=full_configs['anylog_server_port'],
                                                exception=args.exception):
        print(blockchain_calls.create_anylog_policy(policy_type='master', name=full_configs['node_name'],
                                                    hostname=full_configs['hostname'],
                                                    external_ip=full_configs['external_ip'], local_ip=full_configs['ip'],
                                                    anylog_server_port=full_configs['anylog_server_port'],
                                                    anylog_rest_port=full_configs['anylog_rest_port'],
                                                    company=full_configs['company_name'], exception=args.exception))

    # cluster
    if not blockchain_calls.check_policy_exists(anylog_conn=anylog_conn, policy_type='cluster',
                                                name=full_configs['cluster_name'], company=full_configs['company_name'],
                                                exception=args.exception):
        print(blockchain_calls.create_anylog_policy(policy_type='cluster', name=full_configs['cluster_name'],
                                                    db_name=full_configs['default_dbms'],
                                                    company=full_configs['company_name'], exception=args.exception))







if __name__ == '__main__':
    standalone()