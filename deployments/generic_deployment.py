import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'python_rest'))


from anylog_connector import AnyLogConnector
import generic_data_calls

def run_mqtt_client(anylog_conn:AnyLogConnector, anylog_configs:dict, exception:bool=False):

    mqtt_log = False

    mqtt_broker = "driver.cloudmqtt.com"
    mqtt_port = 18785
    mqtt_user = None
    mqtt_passwd = None
    mqtt_topic = "anylogedgex"
    mqtt_dbms = "test"
    mqtt_table = "rand_data"
    mqtt_timestamp_column = "now"
    mqtt_value_column = "bring[readings][][value]"
    mqtt_value_column_type = "str"

    if 'mqtt_log' in anylog_configs:
       mqtt_log = anylog_configs['mqtt_log']
    if 'mqtt_broker' in anylog_configs:
        mqtt_broker = anylog_configs['mqtt_broker']
    if 'mqtt_port' in anylog_configs:
        mqtt_port = anylog_configs['mqtt_port']
    if 'mqtt_user' in anylog_configs:
        mqtt_user = anylog_configs['mqtt_user']
    if 'mqtt_passwd' in anylog_configs:
        mqtt_passwd = anylog_configs['mqtt_passwd']
    if 'mqtt_topic' in anylog_configs:
        mqtt_topic = anylog_configs['mqtt_topic']
    if 'mqtt_dbms' and anylog_configs:
        mqtt_dbms = anylog_configs['mqtt_dbms']
    if 'mqtt_table' in anylog_configs:
        mqtt_table = anylog_configs['mqtt_table']
    if 'mqtt_timestamp_column' in anylog_configs:
        mqtt_timestamp_column = anylog_configs['mqtt_timestamp_column']
    if 'mqtt_value_column' in anylog_configs:
        mqtt_value_column = anylog_configs['mqtt_value_column']
    if 'mqtt_value_column_type' in anylog_configs:
        mqtt_value_column_type = anylog_configs['mqtt_value_column_type']

    if generic_data_calls.run_mqtt_client(anylog_conn=anylog_conn, broker=mqtt_broker, port=mqtt_port,
                                          username=mqtt_user, password=mqtt_passwd, topic=mqtt_topic, db_name=mqtt_dbms,
                                          table_name=mqtt_table,timestamp=mqtt_timestamp_column,
                                          values={'value': {
                                              'type': mqtt_value_column_type,
                                              'value': mqtt_value_column
                                          }},
                                          logs=mqtt_log, user_agent=False, view_help=False,
                                          exception=exception) is False:
        print(f'Notice: Failed to add mqtt topic {mqtt_topic}')
