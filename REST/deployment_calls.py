from anylog_connection import AnyLogConnection
from support import *

def run_mqtt_client(anylog_conn:AnyLogConnection, broker:str, port:str, mqtt_user:str='', mqtt_passd:str='',
                    mqtt_log:bool=False, topic_name:str='*', topic_dbms:str='', topic_table:str='',
                    columns:dict={}, exception:bool=False)->bool:
    """
    Run MQTT client
    :command:
        run mqtt client where broker=!broker and port=!port and user-agent=anylog and user=!mqtt_user and password=!mqtt_password and log=!mqtt_log and topic=(name=!mqtt_topic_name and dbms=!mqtt_topic_dbms and table=!mqtt_topic_table and column.timestamp.timestamp=!mqtt_column_timestamp and column.value=(value=!mqtt_column_value and type=!mqtt_column_value_type))
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        broker:str - broker connection information
        port:str - port correlated to broker
        mqtt_user:str - user for accessing MQTT
        mqtt_passswd:str - password correlated to user
        mqtt_log:bool - whether to print MQTT logs or not
        topic_name:str - MQTT topic
        topic_dbms:str - database
        topic_name:str - table
        columns:dict - columns to extract
            {
                "timestamp": {"value": "bring [ts]", "type": "timestamp"},
                "value": {"value": "bring [value]", "type": "float"}
            }
        exception:bool - whether to print exception
    :params:
        cmd:str - MQTT command to execute
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    cmd = format_mqtt_cmd(broker=broker, port=port, mqtt_user=mqtt_user, mqtt_passd=mqtt_passd, mqtt_log=mqtt_log,
                          topic_name=topic_name, topic_dbms=topic_dbms, topic_table=topic_table, columns=columns)
    headers = {
        "command": cmd,
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def set_threshold(anylog_conn:AnyLogConnection, write_immediate:bool=True, exception:bool=False)->bool:
    """
    Set buffer threshold
    :command:
        set buffer threshold where write_immediate = true
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        write_immediate:bool - whether to set threshold to immediate
        exception:bool - whether to print exception
    :params:
        cmd:str - command to execute
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    cmd = "set buffer threshold"
    if write_immediate is True:
        cmd += " where write_immediate=true"
    headers = {
        "command": cmd,
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def run_streamer(anylog_conn:AnyLogConnection, exception:bool=False)->bool:
    """
    Set streamer
    :command:
        run streamer
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    headers = {
        "command": "run streamer",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def run_operator(anylog_conn:AnyLogConnection, create_table:bool=True, update_tsd_info:bool=True, archive:bool=True,
                 distributor:bool=True, master_node:str="!master_node", exception:bool=False)->bool:
    """
    Start Operator process
    :command:
        run operator where create_table=true and update_tsd_info=true and archive=true and distributor=true and master_node=!master_node
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        create_table:bool - Whether to create/declare table if DNE
        update_tsd_info:str - Whether to update tsd_info table
        archive:str - whether to archive (or backup) files
        distributor:str - whether to distribute data among other operators in the cluster
         master_node:str - which master to work against
        exception:bool - whether to print exception
    :params:
        cmd:str - command to execute
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    cmd = f"run operator where create_table=true and update_tsd_info=true and archive=true and distributor=true and master_node={master_node}"
    if create_table is False:
        cmd = cmd.replace("create_table=true", "create_table=false")
    if update_tsd_info is False:
        cmd = cmd.replace("update_tsd_info=true", "update_tsd_info=false")
    if archive is False:
        cmd = cmd.replace("archive=true", "archive=false")
    if distributor is False:
        cmd = cmd.replace("distributor=true", "distributor=false")

    headers = {
        "command": cmd,
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r