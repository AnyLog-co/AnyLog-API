import argparse
import os
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).split('deployment_scripts')[0]
REST_PATH = os.path.join(ROOT_PATH, 'REST')
sys.path.insert(0, REST_PATH)

from anylog_connection import AnyLogConnection
import authentication
import blockchain_calls
import database_calls
import deployment_calls
import generic_get_calls
import generic_post_calls
import support

def main():
    """
    The following is intended as an example of deploying Master Node with blockchain policy declaration(s).
    :positional arguments:
        conn                  REST IP/Port connection to work against
    :optional arguments:
        -h, --help                  show this help message and exit
        --auth      AUTH            Authentication (user, passwd) for node
        --timeout   TIMEOUT         REST timeout
        --exception [EXCEPTION]     whether to print exception
    :params:
        anylog_conn:AnyLogConnection - connection to AnyLog via REST
        anylog_dictionary:dict - dictionary of AnyLog params
        hostname:str - node hostname (added if not in dictionary)
        node_id:str - node ID
        policy_values:dict - policy params

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('conn',         type=str,   default='127.0.0.1:2049', help='REST IP/Port connection to work against')
    parser.add_argument('--auth',       type=tuple, default=(), help='Authentication (user, passwd) for node')
    parser.add_argument('--timeout',    type=int,   default=30, help='REST timeout')
    parser.add_argument('--exception',  type=bool,  nargs='?',  const=True, default=False, help='whether to print exception')
    args = parser.parse_args()

    anylog_conn = AnyLogConnection(conn=args.conn, auth=args.auth, timeout=args.timeout)

    # validate status
    print("Validate Connection")
    if not generic_get_calls.validate_status(anylog_conn=anylog_conn, exception=args.exception):
        print(f'Failed to validate connection to AnyLog on {anylog_conn.conn}')
        exit(1)

    anylog_dictionary = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, exception=args.exception)
    authentication.disable_authentication(anylog_conn=anylog_conn, exception=args.exception)

    # set home path & create work dirs
    print("Set Directories")
    generic_post_calls.set_home_path(anylog_conn=anylog_conn, anylog_root_dir=anylog_dictionary['anylog_path'],
                                     exception=args.exception)
    generic_post_calls.create_work_dirs(anylog_conn=anylog_conn, exception=args.exception)

    print("Set Params & Extract Dictionary")
    if 'hostname' not in anylog_dictionary:
        hostname = generic_get_calls.get_hostname(anylog_conn=anylog_conn, exception=args.exception)
        if hostname != '':
            generic_post_calls.set_variables(anylog_conn=anylog_conn, key='hostname', value=hostname,
                                             exception=args.exception)

    node_id = authentication.get_node_id(anylog_conn=anylog_conn, exception=args.exception)

    if not isinstance(node_id, str):
        authentication.create_public_key(anylog_conn=anylog_conn, password='passwd', exception=args.exception)
        node_id = authentication.get_node_id(anylog_conn=anylog_conn, exception=args.exception)
    generic_post_calls.set_variables(anylog_conn=anylog_conn, key='node_id', value=node_id, exception=args.exception)

    print("Connect Databases & Table(s)")
    for db_name in ['blockchain', 'system_query', 'almgm', anylog_dictionary['default_dbms']]:
        while db_name not in database_calls.get_dbms(anylog_conn=anylog_conn, exception=args.exception):
            if anylog_dictionary['db_type'] == 'sqlite':
                database_calls.connect_dbms(anylog_conn=anylog_conn, db_name=db_name, db_type='sqlite')
            else:
                database_calls.connect_dbms(anylog_conn=anylog_conn, db_name=db_name, db_type="!db_type",
                                            db_ip="!db_ip", db_port="!db_port", db_user="!db_user",
                                            db_passwd="!db_passwd", exception=args.exception)
            if db_name not in database_calls.get_dbms(anylog_conn=anylog_conn, exception=args.exception):
                anylog_dictionary['db_type'] = 'sqlite'

            if db_name == 'blockchain' and not database_calls.check_table(anylog_conn=anylog_conn, db_name=db_name,
                                                                          table_name='ledger', exception=args.exception):
                database_calls.create_table(anylog_conn=anylog_conn, db_name='blockchain', table_name='ledger',
                                            exception=args.exception)
            elif db_name == 'almgm' and not database_calls.check_table(anylog_conn=anylog_conn, db_name=db_name,
                                                                       table_name='tsd_info', exception=args.exception):
                database_calls.create_table(anylog_conn=anylog_conn, db_name='almgm', table_name='tsd_info',
                                            exception=args.exception)

    print("Set Schedulers")
    get_processes = generic_get_calls.get_processes(anylog_conn=anylog_conn, exception=args.exception)
    generic_post_calls.run_scheduler1(anylog_conn=anylog_conn, exception=args.exception)
    if get_processes['Blockchain Sync']['Status'] == 'Not declared':

        generic_post_calls.blockchain_sync_scheduler(anylog_conn=anylog_conn, source="master",
                                                     time="!sync_time", dest="!dest",
                                                     connection="!master_node", exception=args.exception)

    print('Declare Policies')
    # master
    if not blockchain_calls.blockchain_get(anylog_conn=anylog_conn, policy_type='master',
                                           where_condition=("name=!node_name and company=!company_name and "
                                                   +"ip=!external_ip and port=!anylog_server_port"),
                                           bring_condition=None, separator=None, exception=args.exception):

        policy_values = {
            "hostname": anylog_dictionary['hostname'],
            "name": anylog_dictionary['node_name'],
            "ip" : anylog_dictionary['external_ip'],
            "local_ip": anylog_dictionary['ip'],
            "company": anylog_dictionary['company_name'],
            "port": int(anylog_dictionary['anylog_server_port']),
            "rest_port": int(anylog_dictionary['anylog_rest_port']),
            "loc": anylog_dictionary['location']
        }

        policy = support.build_policy(policy_type="master", company_name=anylog_dictionary['company_name'],
                                      policy_values=policy_values)
        blockchain_calls.declare_policy(anylog_conn=anylog_conn, policy=policy,
                                        master_node=anylog_dictionary['master_node'], exception=False)

    # cluster
    cluster_policy = blockchain_calls.blockchain_get(anylog_conn=anylog_conn, policy_type='cluster',
                                                     where_condition="name=!cluster_name and company=!company_name",
                                                     bring_param="first", separator=None,
                                                     exception=args.exception)
    if not cluster_policy:
        try:
            db_name = anylog_dictionary['default_dbms']
        except:
            db_name = 'aiops'
        policy_values = {
            "name": anylog_dictionary['cluster_name'],
            "company": anylog_dictionary['company_name'],
            "dbms": db_name,
            "master": anylog_dictionary['master_node']
        }
        policy = support.build_policy(policy_type="cluster", company_name=anylog_dictionary['company_name'],
                                      policy_values=policy_values)
        blockchain_calls.declare_policy(anylog_conn=anylog_conn, policy=policy,
                                        master_node=anylog_dictionary['master_node'], exception=False)
        cluster_policy = blockchain_calls.blockchain_get(anylog_conn=anylog_conn, policy_type='cluster',
                                                         where_condition="name=!cluster_name and company=!company_name",
                                                         bring_param="first", separator=None,
                                                         exception=args.exception)

    # operator
    if not blockchain_calls.blockchain_get(anylog_conn=anylog_conn, policy_type='operator',
                                           where_condition=("name=!node_name and company=!company_name and "
                                                            + "ip=!external_ip and port=!anylog_server_port"),
                                           bring_condition=None, separator=None, exception=args.exception):
        policy_values = {
            "hostname": anylog_dictionary['hostname'],
            "name": anylog_dictionary['node_name'],
            "ip" : anylog_dictionary['external_ip'],
            "local_ip": anylog_dictionary['ip'],
            "company": anylog_dictionary['company_name'],
            "port": int(anylog_dictionary['anylog_server_port']),
            "rest_port": int(anylog_dictionary['anylog_rest_port']),
            "loc": anylog_dictionary['location']
        }
        if cluster_policy:
            policy_values['cluster'] = cluster_policy[0]['cluster']['id']
        policy = support.build_policy(policy_type="operator", company_name=anylog_dictionary['company_name'],
                                      policy_values=policy_values)

        blockchain_calls.declare_policy(anylog_conn=anylog_conn, policy=policy,
                                        master_node=anylog_dictionary['master_node'], exception=args.exception)

    print('Set Partitions')
    if database_calls.check_partitions(anylog_conn=anylog_conn, exception=args.exception) is False:
        database_calls.set_partitions(anylog_conn=anylog_conn, db_name=anylog_dictionary['default_dbms'],
                                      table=anylog_dictionary['partition_table'],
                                      partition_column=anylog_dictionary['partition_column'],
                                      partition_interval=anylog_dictionary['partition_interval'],
                                      exception=args.exception)
        drop_partition_task = (f"drop partition where dbms={anylog_dictionary['default_dbms']} "
                               +f"and table={anylog_dictionary['partition_table']} "
                               +f"and keep={anylog_dictionary['partition_keep']}")
        generic_post_calls.schedule_task(anylog_conn=anylog_conn, time=anylog_dictionary['partition_sync'],
                                         name="Remove Old Partitions", task=drop_partition_task, exception=args.exception)

    print('Set MQTT')
    if anylog_dictionary['enable_mqtt'] == 'true':
        mqtt_user = ""
        mqtt_passwd = ""
        if 'mqtt_user' in anylog_dictionary:
            mqtt_user = anylog_dictionary['mqtt_user']
        if 'mqtt_passwd' in anylog_dictionary:
            mqtt_passwd = anylog_dictionary['mqtt_passwd']

        deployment_calls.run_mqtt_client(anylog_conn=anylog_conn, broker=anylog_dictionary['broker'],
                                         mqtt_user=mqtt_user, mqtt_passwd=mqtt_passwd,
                                         port=anylog_dictionary['mqtt_port'], mqtt_log=anylog_dictionary['mqtt_log'],
                                         topic_name=anylog_dictionary['mqtt_topic_name'],
                                         topic_dbms=anylog_dictionary['mqtt_topic_dbms'],
                                         topic_table=anylog_dictionary['mqtt_topic_table'],
                                         columns={
                                             "timestamp": {
                                                 "value": anylog_dictionary['mqtt_column_timestamp'],
                                                 "type": "timestamp"
                                             },
                                             "value": {
                                                 "value": anylog_dictionary['mqtt_column_value'],
                                                 'type': anylog_dictionary['mqtt_column_value_type']
                                             }
                                         },
                                         exception=args.exception)

    print("Start Operator")
    deployment_calls.set_threshold(anylog_conn=anylog_conn, write_immediate=anylog_dictionary['write_immediate'],
                                   exception=args.exception)
    if get_processes['Streamer']['Status'] == 'Not declared':
        deployment_calls.run_streamer(anylog_conn=anylog_conn, exception=args.exception)
    if get_processes['Distributor']['Status'] == 'Not declared':
        deployment_calls.data_distributor(anylog_conn=anylog_conn, exception=args.exception)


    if get_processes['Operator']['Status'] == 'Not declared':
        policy = blockchain_calls.blockchain_get(anylog_conn=anylog_conn, policy_type='operator',
                                                 where_condition=("name=!node_name and company=!company_name and "
                                                                  + "ip=!external_ip and port=!anylog_server_port"),
                                                 bring_condition=None, separator=None, exception=args.exception)

        deployment_calls.run_operator(anylog_conn=anylog_conn, policy_id=policy[0]['operator']['id'],
                                      create_table=anylog_dictionary['create_table'],
                                      update_tsd_info=anylog_dictionary['update_tsd_info'],
                                      archive=anylog_dictionary['archive'],
                                      distributor=anylog_dictionary['distributor'],
                                      master_node=anylog_dictionary['master_node'], exception=args.exception)



if __name__ == '__main__':
    main()