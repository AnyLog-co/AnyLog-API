from anylog_connection import AnyLogConnect


def __print_error(cmd, error:str):
    """
    Print Error message
    :args:
        error:str - error message
    :print:
        error message
    """
    if isinstance(error, int):
        print(f'Failed to execute "{cmd}" (Network Error: {error})')
    else:
        print(f'Failed to execute "{cmd}" (Error: {e})')


def __format_mqtt_cmd(broker:str, port:str, mqtt_user:str='', mqtt_passd:str='', mqtt_log:bool=False,
                      topic_name:str='*', topic_dbms:str='', topic_table:str='', columns:dict={})->str:
    """
    Given the params for an MQTT generate MQTT call
    :args:
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
    :params:
        cmd:str - full MQTT call
        topic:str - topic component for MQTT call
    :return:
        cmd
    """
    cmd = f"run mqtt client where broker={broker} and port={port}"
    if mqtt_user != '' and mqtt_passd != '':
        cmd += f" and user={mqtt_user} and password={mqtt_passd}"
    if broker == 'rest':
        cmd += " and user-agent=anylog"
    cmd += " and log=false"
    if mqtt_log is True:
        cmd = cmd.replace('false', 'true')
    topic = f"name={topic_name}"
    if topic_dbms != '':
        topic += f" and dbms={topic_dbms}"
    if topic_table != '':
        topic += f" and table={topic_name}"
    if columns != {} :
        for column in columns:
            if columns[column]['type'] not in ['str', 'int', 'float', 'bool', 'timestamp']:
                columns[column]['type'] = 'str'
            topic += f" and column.{column}=(value={columns[column]['value']} and type={columns[column]['type']})"
    cmd += f" and topic=({topic})"
    return cmd


def set_home_path(anylog_conn:AnyLogConnect, anylog_root_dir:str="!anylog_root_dir", excetion:bool=False)->bool:
    """
    The following sets the home root path
    :command:
        set anylog home !anylog_root_dir
    :args:
        anylog_conn:AnyLogConnect - connection to AnyLog
        anylog_root_dir:str - AnyLog root dir path
        exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    headers ={
        'command': f'set anylog home {anylog_root_dir}',
        'User-Agent': 'AnyLog/1.23'
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        __print_error(cmd=headers['command'], error=error)
    return r


def connect_dbms(anylog_conn:AnyLogConnect, db_name:str, db_type:str="sqlite", db_ip:str="!db_ip", db_port:str="!db_port",
                 db_user:str="!db_user", db_passwd:str="!db_passwd", exception:bool=False)->bool:
    """
    Connect to logical database
    :command: 
        connect dbms blockchain where type=psql and user = !db_user and password = !db_passwd and ip = !db_ip and port = !db_port
    :args:
        anylog_conn:AnyLogConnect - connection to AnyLog
        db_name:str - logical database name
        db_type:str - logical database type (ex SQLite or PSQL)
        db_ip:str - database IP address
        db_port:str - database port
        db_user:str - database user
        db_passwd:str - password correlated to database user
        exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    cmd = f"connect dbms {db_name} where type={db_type}"
    if db_type != 'sqlite':
        cmd += f" and ip={db_ip} and port={db_port} and user={db_user} and password=${db_passwd}"
    headers ={
        'command': cmd,
        'User-Agent': 'AnyLog/1.23'
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        __print_error(cmd=headers['command'], error=error)
    return r


def run_scheduler1(anylog_conn:AnyLogConnect, exception:bool=False)->bool:
    """
    Run base scheduler
    :command:
        run scheduler 1
    :args:
        anylog_conn:AnyLogConnect - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    headers = {
        "command": "run scheduler 1",
        "User-Agent": "AnyLog/1.23"
    }

    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        __print_error(cmd=headers['command'], error=error)
    return r


def blockchain_sync_scheduler(anylog_conn:AnyLogConnect, source:str="master", time:str="!sync_time", dest:str="file",
                              connection:str="!master_node", exception:bool=False)->bool:
    """
    Set blockchain sync process
    :command:
        run blockchain sync where source=master and time=!sync_time and dest=file and connection=!master_node
    :args:
        anylog_conn:AnyLogConnect - connection to AnyLog
        source:str - blockchain source
        time:str - how often to sync blockchain
        dest:str - destination of copy of blockchain
        connection:str - REST connection info
        exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    headers = {
        "command": f"run blockchain sync where source={source} and time={time} and dest={dest} and connection={connection}",
        "User-Agent": "AnyLog/1.23"
    }

    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        __print_error(cmd=headers['command'], error=error)
    return r


def schedule_task(anylog_conn:AnyLogConnect, time:str, name:str, task:str, exception:bool=False)->bool:
    """
    Execute Task
    :command:
        schedule time = 1 day and name = "Remove Old Partitions" task drop partition where dbms=!default_dbms and table =!table_name and keep=!partition_keep
    :args:
       anylog_conn:AnyLogConnect - connection to AnyLog
       time:str - how often to run the task
       name:str - task name
       task:str - The actual task to run
       exception:bool - whether to print exception
    :params:

    """
    headers = {
        "command": f"schedule time={time} and name={name} task {task}",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        __print_error(cmd=headers['command'], error=error)
    return r


def set_partitions(anylog_conn:AnyLogConnect, db_name:str="!default_dbms", table:str="*",
                   partition_column:str="!partition_column", partition_interval:str="!partition_interval",
                   exception:bool=False)->bool:
    """
    Set partitions
    :command:
        partition !default_dbms * using !partition_column by !partition_interval
    :args:
        anylog_conn:AnyLogConnect - connection to AnyLog
        db_name:str - logical database to partition
        table:str - table to partition against, if set to '*' partition all tables in database
        partition_column:str - column to partition by
        partition_interval:str - partition interval
        exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    headers = {
        "command": f"partition {db_name} {table} using {partition_column} by {partition_interval}",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        __print_error(cmd=headers['command'], error=error)
    return r


def run_mqtt_client(anylog_conn:AnyLogConnect, broker:str, port:str, mqtt_user:str='', mqtt_passd:str='',
                    mqtt_log:bool=False, topic_name:str='*', topic_dbms:str='', topic_table:str='',
                    columns:dict={}, exception:bool=False)->bool:
    """
    Run MQTT client
    :command:
        run mqtt client where broker=!broker and port=!port and user-agent=anylog and user=!mqtt_user and password=!mqtt_password and log=!mqtt_log and topic=(name=!mqtt_topic_name and dbms=!mqtt_topic_dbms and table=!mqtt_topic_table and column.timestamp.timestamp=!mqtt_column_timestamp and column.value=(value=!mqtt_column_value and type=!mqtt_column_value_type))
    :args:
        anylog_conn:AnyLogConnect - connection to AnyLog
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
    cmd = __format_mqtt_cmd(broker=broker, port=port, mqtt_user=mqtt_user, mqtt_passd=mqtt_passd, mqtt_log=mqtt_log,
                            topic_name=topic_name, topic_dbms=topic_dbms, topic_table=topic_table, columns=columns)
    headers = {
        "command": cmd,
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        __print_error(cmd=headers['command'], error=error)
    return r


def set_threshold(anylog_conn:AnyLogConnect, write_immediate:bool=True, exception:bool=False)->bool:
    """
    Set buffer threshold
    :command:
        set buffer threshold where write_immediate = true
    :args:
        anylog_conn:AnyLogConnect - connection to AnyLog
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
        __print_error(cmd=headers['command'], error=error)
    return r


def run_streamer(anylog_conn:AnyLogConnect, exception:bool=False)->bool:
    """
    Set streamer
    :command:
        run streamer
    :args:
        anylog_conn:AnyLogConnect - connection to AnyLog
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
        __print_error(cmd=headers['command'], error=error)
    return r


def run_operator(anylog_conn:AnyLogConnect, create_table:bool=True, update_tsd_info:bool=True, archive:bool=True,
                 distributor:bool=True, master_node:str="!master_node", exception:bool=False)->bool:
    """
    Start Operator process
    :command:
        run operator where create_table=true and update_tsd_info=true and archive=true and distributor=true and master_node=!master_node
    :args:
        anylog_conn:AnyLogConnect - connection to AnyLog
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
        __print_error(cmd=headers['command'], error=error)
    return r