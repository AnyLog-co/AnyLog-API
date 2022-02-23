import os
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).split('anylog_scripts')[0]
REST_PATH = os.path.join(ROOT_PATH, 'REST')
sys.path.insert(0, REST_PATH)

import rest_call
from anylog_connection import AnyLogConnect


def main(conn:str, auth:tuple=(), timeout:int=30, exception:bool=False):
    """
    :args:
        conn:str - REST IP:PORT for communicating with AnyLog
        auth:tuple - authentication information
        timeout:int - REST timeout (in seconds)
        exception:bool - whether to print exception
    """
    anylog_conn = AnyLogConnect(conn=conn, auth=auth, timeout=timeout)

    # set home path
    rest_call.set_home_path(anylog_conn=anylog_conn, anylog_root_dir="!anylog_root_dir", excetion=exception)

    # connect to logical database(s)
    for db_name in ['blockchain', 'almgm', '!default_dbms', 'system_query']:
        rest_call.connect_dbms(anylog_conn=anylog_conn, db_name=db_name, db_type="psql", db_ip="!db_ip",
                               db_port="!db_port", db_user="!db_user", db_passwd="!db_passwd", exception=exception)

    # Set schedulers
    rest_call.run_scheduler1(anylog_conn=anylog_conn, exception=exception)

    rest_call.blockchain_sync_scheduler(anylog_conn=anylog_conn, source="master", time="!sync_time", dest="file",
                                        connection="!master_node", exception=exception)

    # set partitions
    rest_call.set_partitions(anylog_conn=anylog_conn, db_name="!default_dbms", table="*",
                             partition_column="!partition_column", partition_interval="!partition_interval",
                             exception=exception)
    rest_call.schedule_task(anylog_conn=anylog_conn, time="1 day", name="Remove Old Partitions",
                            task="drop partition where dbms=!default_dbms and table =!table_name and keep=!partition_keep",
                            exception=exception)

    # Set MQTT client
    rest_call.run_mqtt_client(anylog_conn=anylog_conn, broker="!broker", port="!anylog_rest_port",  mqtt_log=False,
                              topic_name="!mqtt_topic_name", topic_dbms="!mqtt_topic_dbms",
                              topic_table="!mqtt_topic_table",
                              columns={"timestamp": {"value": "!mqtt_column_timestamp", "type": "timestamp"},
                                       "value": {"value": "!mqtt_column_value", "type": "!mqtt_column_value_type"}},
                              exception=exception)

    # Start Operator
    rest_call.set_threshold(anylog_conn=anylog_conn, write_immediat=True, exception=exception)
    rest_call.run_streamer(anylog_conn=anylog_conn, exception=exception)
    rest_call.run_operator(anylog_conn=anylog_conn, create_table=True, update_tsd_info=True, archive=True,
                           distributor=True, master_node="!master_node", exception=exception)


if __name__ == '__main__':
    main(conn='127.0.0.1:2049', auth=(), timeout=30, exception=True)