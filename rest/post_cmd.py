import __init__
import rest.anylog_api as anylog_api
import rest.get_cmd as get_cmd
import support.errors as errors

def post_value(conn:anylog_api.AnyLogConnect, key:str, value:str, exception:bool=False)->bool: 
    """
    POST value to dictionary
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        key:str - dictionary key
        value:str - value for corresponding key
        exception:bool - whether or not to print error to screen 
    :param: 
        status:bool
        cmd:str - command to execute
    :return: 
        status
    """
    status = True 
    cmd = "set %s=%s" % (key, value)
    r, error = conn.post(command=cmd)
     
    if errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception) == True:  
        status = False 

    return status 
 
def post_scheduler1(conn:anylog_api.AnyLogConnect, exception:bool=False)->bool: 
    """
    POST scheduler 1 to AnyLog 
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        exception:bool - whether or not to print error to screen 
    :params: 
        status:bool 
        cmd:str: 
    """
    status = True
    cmd = "run scheduler 1" 

    if 'not declared' in get_cmd.get_scheduler(conn=conn, scheduler_name='1', exception=exception): 
        r, error = conn.post(command=cmd)
        if errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception) == True:  
            status = False 

    return status 

def run_publisher(conn:anylog_api.AnyLogConnect, master_node:str, dbms_name:str, table_name:str, compress_json:bool=True, move_json:bool=True, exception:bool=False)->bool:
    """
    Start publisher process
    :args: 
        conn:anylog_api.AnyLogConnect connection to AnyLog
        master_node:str - Master node 
        dbms_name:str - database name 
        table_name:str - table name
        compress_json:bool - compress published file 
        move_json:bool - send file to bkup
        exception:bool - whether or not to print error to screen 
    :params: 
        status:bool 
        cmd:str - command to execute
    :return: 
        status
    """ 
    status = True
    if isinstance(compress_json, bool): 
        compress_json = str(compress_json).lower()
    else: 
        compress_json == 'true'
    if isinstance(move_json, bool): 
        move_json = str(move_json).lower()
    else: 
        move_json = 'true' 

    if 'Not declared' in get_cmd.get_processes(conn=conn, exception=exception).split('Publisher')[-1].split('\r')[0]:
        cmd = 'run publisher where compress_json=%s and move_json=%s and master_node=%s and dbms_name=%s and table_name=%s' % (compress_json, move_json, master_node, dbms_name, table_name)
        r, error = conn.post(command=cmd)
        if errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception) == True:  
            status = False 

    return status 

def set_immidiate_threshold(conn:anylog_api.AnyLogConnect, exception:bool=False)->bool: 
    """
    Set threshold tto immidiate
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        exception:bool - whether or not to print error to screen 
    :params: 
        status:bool 
        cmd:str - command to execute 
    :return: 
        status 
    """
    status = True
    cmd = "set buffer threshold where write_immediate = true"

    r, error = conn.post(command=cmd)
    if errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception) == True: 
        status = False 

    return status 


def run_mqtt(conn:anylog_api.AnyLogConnect, config:dict, exception:bool=False)->bool: 
    """
    Connect to MQTT
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        config:dict - AnyLog configuration
        exception:bool - whether or not to print error to screen 
    :params: 
        status:bool
        cmd:str - command to execute
        frmt:int - for MQTT if dbms and/or table not in topic frmt=1, else frmt=0  
    :mqtt params: 
        broker:str - MQTT broker, if set to RSET utilze MQTT process to format data coming in via REST
        mqtt_user:str - MQTT user 
        mqtt_psswd:str - MQTT password 
        topic:str - MQTT topiic
        dbms:str - database to store data in
        table:str - table to store data in 
    """
    status = True
    # MQTT access params
    if 'mqtt_conn_info' not in config:
        if exception is True:
            print('MQTT connection info required')
    elif config['mqtt_conn_info'] == 'rest':
        cmd = 'run mqtt client where broker=rest and user-agent=anylog'
    else: # user@broker:passwd
        cmd = 'run mqtt client where broker=%s' % config['mqtt_conn_info'].split('@')[-1].split(':')[0]
        if '@' in config['mqtt_conn_info']:
            cmd += ' and user=%s' % config['mqtt_conn_info'].split('@')[0]
        if ':' in config['mqtt_conn_info']:
            cmd += ' and password=%s' % config['mqtt_conn_info'].split(':')[-1]

    if 'mqtt_port' in config:
        cmd += ' and port=%s' % config['mqtt_port']

    if 'mqtt_log' in config:
        cmd += ' and log=%s' % config['mqtt_log']
    else:
        cmd += ' and log=false'

    # topic params
    if 'mqtt_topic_name' not in config:
        config['mqtt_topic_name'] = '#'
    for param in ['mqtt_topic_dbms', 'mqtt_topic_table', 'mqtt_column_timestamp', 'mqtt_column_value_type', 'mqtt_column_value']:
        if param not in config:
            status = False
        elif param == 'mqtt_column_value_type' and config['mqtt_column_value_type'] not in ['str', 'int', 'float', 'bool']:
            config['mqtt_column_value_type'] = 'str'

    if status is False:
        cmd += ' and topic=%s' % config['mqtt_topic_name']
    else:
        execute_cmd = cmd + ' and topic=(name=%s and dbms=%s and table=%s and column.timestamp.timestamp=%s and column.value=(type=%s and value=%s))'
        execute_cmd = execute_cmd % (config['mqtt_topic_name'], config['mqtt_topic_dbms'], config['mqtt_topic_table'],
                     config['mqtt_column_timestamp'], config['mqtt_column_value_type'], config['mqtt_column_value'])

    r, error = conn.post(command=execute_cmd)
    if errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception) == True:
        status = False
    """
    # Bug with function
    if config['enable_other_mqtt'] == 'true' and status is not False and config['mqtt_topic_name'] != '#':
        execute_cmd = cmd + ' and topic="#"'
        r, error = conn.post(command=execute_cmd)
        if errors.post_error(conn=conn.execute_cmd, command=cmd, r=r, error=error, exception=exception) == True:
            status = False
    """
    
    return status
