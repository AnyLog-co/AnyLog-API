import os
import sys 

import get_cmd 
import rest 

support_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/support')) 
sys.path.insert(0, support_dir) 

import errors


def post_value(conn:rest.AnyLogConnect, key:str, value:str, exception:bool=False)->bool: 
    """
    POST value to dictionary
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog
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
 
def post_scheduler1(conn:rest.AnyLogConnect, exception:bool=False)->bool: 
    """
    POST scheduler 1 to AnyLog 
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog
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

def post_publisher(conn:rest.AnyLogConnect, master_node:str, dbms_name:str, table_name:str, compress_json:bool=True, move_json:bool=True, exception:bool=False)->bool: 
    """
    Start publisher process
    :args: 
        conn:rest.AnyLogConnect connection to AnyLog
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

def set_immidiate_threshold(conn:rest.AnyLogConnect, exception:bool=False)->bool: 
    """
    Set threshold tto immidiate
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog
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


def run_mqtt(conn:rest.AnyLogConnct, config:dict, exception:bool=False)->bool: 
    """
    Connect to MQTT
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog
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
    # and topic=(name=foglamp  and dbms=foglamp and table=weather and column.timestamp.timestamp="bring [timestamp]" and column.city.str = "bring [readings][city]" and column.wind_speed.float="bring [readings][wind_speed]" and column.temperature.float="bring [readings][temperature]" and column.humidity.int="bring [readings][humidity]")

    status = True
    cmd = 'run mqtt client where' 

    broker = None
    mqtt_user = None
    mqtt_psswd = None 
    if 'mqtt_conn_info' in config: # format user@broker:password
        broker = config['mqtt_conn_info'].split('@')[-1].split(':') 
        if '@' in config['mqtt_conn_info']:
            mqtt_user = config['mqtt_conn_info'].split('@')[0] 
        if ':' config['mqtt_conn_info']: 
            mqttt_passwd = config['mqtt_conn_info'].split(':')[-1]
        cmd += ' broker=%s' % broker 
    elif 'local_broker' in config and bool(str(config['local_broker']).capitalize()) == True
        broker = 'rest'
        cmd += ' broker=%s' % broker 
    else:
        status = False 

    if broker == 'rest':
        #run mqtt client where broker=rest and user-agent=python 
        cmd += ' and user-agent=python' 
    elif status == True:  
        # run mqtt client where broker=!mqtt_broker and port=!mqtt_broker_port and user=!mqtt_user and password=!mqtt_password
        if 'mqtt_broker_port' in config: 
            cmd += ' and port=%s' config['mqtt_broker_port']
        if mqtt_user != None: 
            cmd += ' and user=%s' % mqtt_user 
        elif mqtt_psswd != None: 
            cmd += ' and password=%s' % mqtt_psswd

    if 'mqtt_log' in config and status == True: 
        cmd += ' and log=%s' % config['mqtt_log']

    # topic
    if status == True: 
        frmt = 0 
        topic = '#'
        dbms = None 
        table = None 
        if 'mqtt_topic_name' in config: 
            topic = config['mqtt_topic_name']
        if 'mqtt_topic_dbms' in config: 
            dbms = config['mqtt_topic_dbms']
        if 'mqtt_topic_table' in config: 
            table = config['mqtt_topic_table']
        if dbms != None and table != None: 
            cmd += ' and topic=(name=%s and dbms=%s and table=%s' % (topic, dbms, table) 
        else: 
            cmd += ' and topic=%s' % topic
            frmt = 1 
        # extract columns  
        if 'mqtt_column_timestamp' in config: 
            if frmt == 0: 
                cmd += ' and column.timestamp.timestamp=%s' % config['mqtt_column_timestamp']
            else: 
                cmd = cmd.replace('topic=%s' % topic, 'topic=(name=%s and column.timestamp.timestamp=%s' % (topic, config['mqtt_column_timestamp']))
                frmt = 0 
        if 'mqtt_column_value' in config: 
            if frmt == 0 and 'mqtt_column_value_type' in config: 
                cmd += ' and column.value
