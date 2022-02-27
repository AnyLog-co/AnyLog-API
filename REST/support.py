import json


def validate_dictionary(anylog_dict:dict={})->dict:
    """
    Validate if needed values exist in dictionary
    if something is miissing, fix it so code will work
    :args:
        anylog_dict:dict - dictionary to validate e
    :return:
        anylog_dict
    """
    # general
    if 'company_name' not in anylog_dict:
        anylog_dict['company_name'] = 'New Company'

    # database [default: sqlite]
    if 'db_type' not in anylog_dict:
        anylog_dict['db_type']='sqlite'
        anylog_dictionary['db_ip'] = None
        anylog_dictionary['db_port'] = None
        anylog_dictionary['db_user'] = None
        anylog_dictionary['db_passwd'] = None
    elif anylog_dict['db_type'] not in ['psql', 'sqlite']:
        anylog_dict['db_type'] = 'sqlite'
    elif anylog_dict['db_type'] == 'psql':
        if 'db_port' not in anylog_dict:
            anylog_dict['db_port'] = 5432
        if 'db_ip' not in anylog_dict or 'db_user' not in anylog_dict or 'db_passwd' not in anylog_dict:
            anylog_dict['db_type'] = 'sqlite'

    # blockchain sync [default: enabled]
    if 'enable_blockchain_sync' not in anylog_dict:
        anylog_dict['enable_blockchain_sync'] = 'true'
    if 'blockchain_source' not in anylog_dict:
        anylog_dict['blockchain_source'] = 'master'
    if 'sync_time' not in anylog_dict:
        anylog_dict['sync_time'] = '30 seconds'
    if 'blockchain_destination' not in anylog_dict:
        anylog_dict['blockchain_destination'] = 'file'
    if 'master_node' not in anylog_dict:
        anylog_dict['master_node'] = f"127.0.0.1:{anylog_dict['anylog_server_port']}"

    # partitioning
    if 'enable_partitions' in anylog_dict and anylog_dict['enable_partitions'] == 'true':
        if 'partition_table' not in anylog_dict:
            anylog_dict['partition_table'] = '*'
        if 'partition_column' not in anylog_dict:
            anylog_dict['partition_column'] = 'timestamp'
        if 'partition_interval' not in anylog_dict['partition_interval']:
            anylog_dict['partition_interval'] = '15 days'
        if 'partition_keep' not in anylog_dict['partition_keep']:
            anylog_dict['partition_keep'] = 6 # ~3 months
        if 'partition_sync' not in anylog_dict['partition_sync']:
            anylog_dict['partition_sync'] = '1 day'
    else:
        anylog_dict['enable_partitions'] = 'false'

    # MQTT
    if 'enable_mqtt' in anylog_dict and anylog_dict['enable_mqtt'] == 'true':
        if 'broker' not in anylog_dict or 'mqtt_port' not in anylog_dict:
            anylog_dict['enable_mqtt'] = 'false'

    # MQTT configs
    if anylog_dict['enable_mqtt'] == 'true':
        if 'mqtt_log' not in anylog_dict:
            anylog_dict['mqtt_log'] = 'false'
        elif anylog_dict['mqtt_log'] != 'false' and anylog_dict['mqtt_log'] != 'true':
            anylog_dict['mqtt_log'] = 'false'
        if 'mqtt_user' not in anylog_dict:
            anylog_dict['mqtt_user'] = ''
        if 'mqtt_passwd' not in anylog_dict:
            anylog_dict['mqtt_passwd'] = ''
        if 'topic_name' not in anylog_dict:
            anylog_dict['topic_name'] = '*'

    return anylog_dict


def print_error(error_type:str, cmd:str, error:str):
    """
    Print Error message
    :args:
        error_type:str - Error Type
        cmd:str - command that failed
        error:str - error message
    :print:
        error message
    """
    if isinstance(error, int): 
        print(f'Failed to execute {error_type} for "{cmd}" (Network Error: {error})')
    else:
        print(f'Failed to execute {error_type} for "{cmd}" (Error: {e})')


def format_mqtt_cmd(broker:str, port:str, mqtt_user:str='', mqtt_passd:str='', mqtt_log:bool=False,
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
        topic += f' and dbms="{topic_dbms}"'
    if topic_table != '':
        topic += f' and table="{topic_table}"'
    if columns != {} :
        for column in columns:
            if columns[column]['type'] not in ['str', 'int', 'float', 'bool', 'timestamp']:
                columns[column]['type'] = 'str'
            if columns[column]['type'] == 'timestamp':
                topic += f' and column.{column}.timestamp="%s"' % columns[column]['value']
            else:
                topic += f' and column.{column}=(value="%s" and type=%s)' % (columns[column]['value'], columns[column]['type'])
    cmd += f" and topic=({topic})"
    return cmd


def read_file(file_name:str, exception:bool=False)->dict:
    """
    Read content in file
    :args:
        file_name:str - file to extract content from
    :params:
        file_content:dict - content in autoexec file
    :return:
        file content
    """
    file_content = {}
    try:
        with open(file_name, 'r') as rf:
            try:
                file_content = json.load(rf)
            except:
                try:
                    file_content = rf.read()
                except Exception as e:
                    if exception is True:
                        print(f"Failed to read content in {file_name} (Error: {e})")
    except Exception as e:
        if exception is True:
            print(f"Failed to open file {file_name} (Error: {e})")

    return file_content
