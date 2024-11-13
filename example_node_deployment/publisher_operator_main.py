import re
import anylog_api.anylog_connector as anylog_connector
import anylog_api.data.database as database_cmds
from example_node_deployment.database import nosql_database
from anylog_api.generic.scheduler import run_schedule_task
import anylog_api.data.management as data_mgmt
from anylog_api.data.publish_data import run_msg_client


def operator_main(conn:anylog_connector.AnyLogConnector, params:dict, operator_id:str, destination:str=None,
                  view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    1. NoSQL database
    2. partition data
    3. clean archive
    4. Threshold
    5. streamer
    6. HA
    7. operator
    """
    blobs_dbms = 'false'
    blobs_folder = 'true'
    compress = 'true'
    reuse_blobs = 'true'
    if 'blobs_reuse' in params:
        blobs_reuse = params['blobs_reuse']

    table_name='*'
    partition_column='insert_timestamp'
    partition_interval='day'
    partition_keep=3
    partition_sync='1 day'
    if 'table_name' in params:
        table_name=params['table_name']
    if 'partition_column' in params:
        partition_column = params['partition_column']
    if 'partition_interval' in params:
        partition_interval=params['partition_interval']
    if 'partition_keep' in params:
        partition_keep=int(params['partition_keep'])
    if 'partition_sync' in params:
        partition_sync = params['partition_sync']

    threshold_time='60 seconds'
    threshold_volume='10KB'
    write_immediate='false'
    if 'threshold_time' in params:
        threshold_time=params['threshold_time']
    if 'threshold_volume' in params:
        threshold_volume=params['threshold_volume']
    if write_immediate in params:
        write_immediate=params['write_immediate']

    archive_delete=30
    if 'archive_delete' in params:
        archive_delete=int(params['archive_delete'])

    create_table=True
    update_tsd_info=True
    archive=True
    archive_sql=True
    compress_json=True
    compress_sql=True
    operator_threads=3
    if 'operator_threads' in params:
        operator_threads=int(params['operator_threads'])

    if 'enable_nosql' in params and params['enable_nosql'] == 'true':
        nosql_database(conn=conn, params=params, destination=destination, view_help=view_help, return_cmd=return_cmd,
                       exception=exception)
        blobs_dbms = 'true'


    data_mgmt.blobs_archiver(conn=conn, blobs_dbms=blobs_dbms, blobs_folder=blobs_folder, compress=compress,
                             reuse_blobs=reuse_blobs, destination=destination, view_help=view_help,
                             return_cmd=return_cmd, exception=exception)

    database_cmds.set_data_partition(conn=conn, db_name=params['default_dbms'], table_name=table_name,
                                     partition_column=partition_column, partition_interval=partition_interval,
                                     destination=destination, view_help=view_help, return_cmd=return_cmd,
                                     exception=exception)

    drop_data_partition_cmd = database_cmds.drop_data_partition(conn=conn, db_name=params['default_dbms'],
                                                                table_name=table_name, partition_keep=partition_keep,
                                                                destination=destination, view_help=view_help,
                                                                return_cmd=True, exception=exception)
    run_schedule_task(conn=conn, name="Drop Partition", time_interval=partition_sync, task=drop_data_partition_cmd,
                      destination=destination, view_help=view_help, return_cmd=return_cmd, exception=exception)

    clean_archive_cmd = data_mgmt.clean_archive_files(conn=conn, archive_delete=archive_delete, destination=destination,
                                                      view_help=view_help, return_cmd=True, exception=exception)


    data_mgmt.buffer_threshold(conn=conn, th_time=threshold_time, th_volume=threshold_volume,
                               write_immediate=write_immediate, destination=destination, view_help=view_help,
                               return_cmd=return_cmd, exception=exception)
    run_schedule_task(conn=conn, name="Drop Archive Files", time_interval='1 day', task=clean_archive_cmd,
                      destination=destination, view_help=view_help, return_cmd=return_cmd, exception=exception)

    data_mgmt.set_streamer(conn=conn, destination=destination, view_help=view_help, return_cmd=return_cmd,
                           exception=exception)


    if 'enable_ha' in params and params['enable_ha'] ==  'true':
        start_data = '-30d'
        if 'start_date' in params:
            start_data=params['start_data']
        if isinstance(start_data, int):
            start_data = f"-{start_data}d"
        elif not re.match(start_data, r"^-?\d+d$"):
            start_data='-30d'

        data_mgmt.data_distributor(conn=conn, destination=destination, view_help=view_help, return_cmd=return_cmd,
                                   exception=exception)
        data_mgmt.data_consumer(conn=conn, start_data=start_data, destination=destination, view_help=view_help,
                                return_cmd=return_cmd, exception=exception)


    data_mgmt.run_operator(conn=conn, operator_id=operator_id, create_table=create_table,
                           update_tsd_info=update_tsd_info, archive_json=archive, compress_json=compress_json,
                           archive_sql=archive_sql, compress_sql=compress_sql, ledger_conn=params['ledger_conn'],
                           threads=operator_threads, destination=destination, view_help=view_help,
                           return_cmd=return_cmd, exception=exception)

    if 'enable_mqtt' in params and params['enable_mqtt'] == 'true':
        mqtt_client(conn=conn, params=params, destination=destination, view_help=view_help, return_cmd=return_cmd,
                    exception=exception)


def mqtt_client(conn:anylog_connector.AnyLogConnector, params:dict, is_rest_broker:bool=False,  destination:str=None,
                view_help:bool=False, return_cmd:bool=False, exception:bool=False):

    mqtt_broker = params['mqtt_broker']
    mqtt_port = int(params['mqtt_port'])
    mqtt_user = None
    mqtt_passwd = None
    mqtt_log = params['mqtt_log']

    if 'mqtt_user' in params:
        mqtt_user = params['mqtt_user']
    if 'mqtt_passwd' in params:
        mqtt_passwd = params['mqtt_passwd']

    msg_topic = params['msg_topic']
    msg_dbms = params['default_dbms']
    msg_timestamp_column="now"
    msg_value_column_type='string'
    if 'msg_dbms' in params:
        msg_dbms = params['msg_dbms']
    msg_table = params['msg_table']
    if 'msg_timestamp_column' in params:
        msg_timestamp_column = params['msg_timestamp_column']
    msg_value_column = params['msg_value_column']
    if 'msg_value_column_type' in params:
        msg_value_column_type = params['msg_value_column_type']

    values = {
        "timestamp": {"type": "timestamp", "value": msg_timestamp_column},
        "value": {"type": msg_value_column_type, "value": msg_value_column.replace("'",'"')}
    }


    run_msg_client(conn=conn, broker=mqtt_broker, port=mqtt_port, username=mqtt_user, password=mqtt_passwd,
                   topic=msg_topic, db_name=msg_dbms, table_name=msg_table, is_rest_broker=is_rest_broker,
                   values=values, destination=destination, view_help=view_help, return_cmd=return_cmd,
                   exception=exception)


