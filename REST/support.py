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