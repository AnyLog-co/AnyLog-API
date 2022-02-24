import os
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).split('anylog_scripts')[0]
REST_PATH = os.path.join(ROOT_PATH, 'REST')
sys.path.insert(0, REST_PATH)

from anylog_connection import AnyLogConnection
import authentication
import database_calls
import deployment_calls
import generic_get_calls
import generic_post_calls


def main(conn:str, auth:tuple=(), timeout:int=30, exception:bool=False):
    """
    The following is intended as an example of deploying Single-Node instance via REST.
    :note:
        When a node is first deployed a user should run part2.py to configure the node agianst the blockchain and
        set unchanged parameters within the node
    :args:
        conn:str - REST IP:PORT for communicating with AnyLog
        auth:tuple - authentication information
        timeout:int - REST timeout (in seconds)
        exception:bool - whether to print exception
    :params:
        anylog_conn:AnyLogConnection - connection to AnyLog via REST
        anylog_dictionary:dict - dictionary of AnyLog params
        drop_partition_task:str - command for dropping partition
        # database creation specific params
        db_status:bool - whether or not database exists
        db_type:str - database type
    """
    anylog_conn = AnyLogConnection(conn=conn, auth=auth, timeout=timeout)

    # validate status
    print("Validate Connection")
    if not generic_get_calls.validate_status(anylog_conn=anylog_conn, exception=exception):
        print(f'Failed to validate connection to AnyLog on {anylog_conn.conn}')
        exit(1)

    authentication.disable_authentication(anylog_conn=anylog_conn, exception=exception)

    # set home path & create work dirs
    print("Set Directories")
    generic_post_calls.set_home_path(anylog_conn=anylog_conn, anylog_root_dir=anylog_dictionary['anylog_root_dir'],
                                     exception=exception)
    generic_post_calls.create_work_dirs(anylog_conn=anylog_conn, exception=exception)

    # Set AnyLog params & extract them
    print("Set Params & Extract Dictionary")
    hostname = generic_get_calls.get_hostname(anylog_conn=anylog_conn, exception=exception)
    if hostname != '':
        generic_post_calls.set_variables(anylog_conn=anylog_conn, key='hostname', value=hostname, exception=exception)

    node_id = authentication.get_node_id(anylog_conn=anylog_conn, exception=exception)
    if not isinstance(node_id, str):
        while int(node_id.status_code) != 200:
            authentication.create_public_key(anylog_conn=anylog_conn, password='passwd', exception=exception)
            node_id = authentication.get_node_id(anylog_conn=anylog_conn, exception=exception)
    generic_post_calls.set_variables(anylog_conn=anylog_conn, key='node_id', value=node_id, exception=exception)

    anylog_dictionary = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, exception=exception)

    """
    connect to logical database(s) - if fails to connect reattempt using SQLite.
    """
    print("Connect to Databases")
    for db_name in ['blockchain', 'almgm', anylog_dictionary['default_dbms'], 'system_query']:
        while db_name not in database_calls.get_dbms(anylog_conn=anylog_conn, exception=exception):
            database_calls.connect_dbms(anylog_conn=anylog_conn, db_name=db_name, db_type=anylog_dictionary['db_type'],
                                        db_ip=anylog_dictionary['db_port'], db_port=anylog_dictionary['db_port'],
                                        db_user=anylog_dictionary['db_user'],
                                        db_passwd=anylog_dictionary['default_dbms'], exception=exception)
            if db_name not in database_calls.get_dbms(anylog_conn=anylog_conn, exception=exception):
                anylog_dictionary['db_type'] = 'sqlite'

        if db_name in database_calls.get_dbms(anylog_conn=anylog_conn, exception=exception) and db_name == 'almgm' and \
                not database_calls.check_table(anylog_conn=anylog_conn, db_name=db_name, table_name='tsd_info',
                                               exception=exception):
            database_calls.create_table(anylog_conn=anylog_conn, db_name='almgm', table_name='tsd_info',
                                        exception=exception)

    # Set schedulers
    print("Set Scheduler(s)")
    generic_post_calls.run_scheduler1(anylog_conn=anylog_conn, exception=exception)

    generic_post_calls.blockchain_sync_scheduler(anylog_conn=anylog_conn, source="master",
                                                 time=anylog_dictionary['sync_time'], dest="file",
                                                 connection=anylog_dictionary['master_node'], exception=exception)

    # set partitions
    print("Set Partitions")
    database_calls.set_partitions(anylog_conn=anylog_conn, db_name=anylog_dictionary['default_dbms'],
                                  table=anylog_dictionary['partition_table'],
                                  partition_column=anylog_dictionary['partition_column'],
                                  partition_interval=anylog_dictionary['partition_interval'],
                                  exception=exception)

    drop_partition_task = f"drop partition where dbms={anylog_dictionary['default_dbms']} and table={anylog_dictionary['partition_table']} and keep={anylog_dictionary['partition_keep']}"
    generic_post_calls.schedule_task(anylog_conn=anylog_conn, time=anylog_dictionary['partition_sync'],
                                     name="Remove Old Partitions", task=drop_partition_task, exception=exception)

    # Set MQTT client
    print("Run MQTT client")
    deployment_calls.run_mqtt_client(anylog_conn=anylog_conn, broker=anylog_dictionary['broker'],
                                     port=anylog_dictionary['anylog_rest_port'],  mqtt_log=False,
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
                                     exception=exception)

    # Start Operator
    print("Start Operatorg")
    deployment_calls.set_threshold(anylog_conn=anylog_conn, write_immediate=True, exception=exception)
    deployment_calls.run_streamer(anylog_conn=anylog_conn, exception=exception)
    deployment_calls.run_operator(anylog_conn=anylog_conn, create_table=True, update_tsd_info=True, archive=True,
                                  distributor=True, master_node=anylog_dictionary['master_node'], exception=exception)


if __name__ == '__main__':
    main(conn='10.0.0.111:2149', auth=(), timeout=30, exception=True)