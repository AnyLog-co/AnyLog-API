"""
The following are generic POST commands often used by AnyLog. Examples:
    * adding a value to dictionary
    * starting a procees such as scheduler
They do not include
    * blockchain processes
    * database processes
    * authentication
"""
import __init__
import anylog_api
import get_cmd
import errors

HEADER = {
    "command": None,
    "User-Agent": "AnyLog/1.23"
}


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
        HEADER:dict - header information
    :return: 
        status
    """
    status = True
    cmd = "set %s=%s" % (key, value)
    if " " in value:
        cmd = cmd.replace(value, '"%s"' % value)
    HEADER['command'] = cmd

    r, error = conn.post(headers=header)
    if errors.print_error(conn=conn.conn, request_type='post', command=cmd, r=r, error=error, exception=exception):
        status = False 

    return status 


def copy_file(conn:anylog_api.AnyLogConnect, remote_node:str, remote_file:str, local_file:str)->bool:
    """
    Copy from one node to another
    :args:
        conn:anylo_api.AnyLogConnect - REST connection to AnyLog, this should be the machine receiving the file(s)
        remote_node:str - TCP IP & port of node sending the files
        remote_file:str - path of remote file
        loccal_file:str - path of local file
    :params:
        status:bool
        header:dict - REST header
    """
    status = True
    if remote_file.startswith('!') and not remote_file.startswith('!!'):
        remote_file = remote_file.replace('!', '!!')
    header['command'] = 'file get %s %s' % (remote_file, local_file)
    header['destination'] == remote_node

    r, error = conn.post(headers=header)
    if errors.print_error(conn=conn.conn, request_type='post', command=header['coommand'], r=r, error=error, exception=exception):
        status = False
    return status


def start_scheduler1(conn:anylog_api.AnyLogConnect, exception:bool=False)->bool:
    """
    POST scheduler 1 to AnyLog 
    :args: 
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        exception:bool - whether or not to print error to screen 
    :params: 
        status:bool 
        HEADER:dict - header information
    """
    status = True
    HEADER['command'] = "run scheduler 1"

    if 'not declared' in get_cmd.get_scheduler(conn=conn, scheduler_name='1', exception=exception): 
        r, error = conn.post(headers=HEADER)
        if errors.print_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception) is True:
            status = False 

    return status 


def run_publisher(conn:anylog_api.AnyLogConnect, master_node:str, dbms_name:str, table_name:str,
                  compress_json:bool=True, move_json:bool=True, exception:bool=False)->bool:
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
        HEADER:dict - header information
        cmd:str - command to execute
    :return: 
        status
    """ 
    status = True
    cmd = 'run publisher where compress_json=%s and move_json=%s and master_node=%s and dbms_name=%s and table_name=%s'

    if isinstance(compress_json, bool):
        compress_json = str(compress_json).lower()
    else: 
        compress_json == 'true'
    if isinstance(move_json, bool) and move_json is not None:
        move_json = str(move_json).lower()
    else: 
        move_json = 'true' 
    HEADER['command'] = cmd % (compress_json, move_json, master_node, dbms_name, table_name)

    if 'Not declared' in get_cmd.get_processes(conn=conn, exception=exception).split('Publisher')[-1].split('\r')[0]:
        r, error = conn.post(headers=HEADER)
        if errors.print_error(conn=conn.conn, request_type='post', command=cmd, r=r, error=error, exception=exception) is True:
            status = False 

    return status 


def run_operator(conn:anylog_api.AnyLogConnect, master_node:str, create_table:bool=True, update_tsd_info:bool=True,
                 archive:bool=True, distributor:bool=True, exception:bool=False)->bool:
    """
    Start Operator process
    :args:
        conn:anylog_api.AnyLogConnect connection to AnyLog
        master_node:str - Master node
        create_table:str - whether to create table
        update_tsd_info;bool - whether to update tsd_info table
        archive:bool - whether to archive data (True) or store in backup (False)
        distributor:bool - distribute the data
        exception:bool - whether or not to print error to screen
    :params:
        status:bool
        cmd:str - command to execute
    :return:
        status
    """
    status = True
    cmd = 'run operator where create_table=%s and update_tsd_info=%s and archive=%s and distributor=%s and master_node=%s'

    if isinstance(create_table, bool):
        create_table = str(create_table).lower()
    else:
        create_table = 'true'
    if isinstance(update_tsd_info, bool):
        update_tsd_info = str(update_tsd_info).lower()
    else:
        update_tsd_info = 'true'
    if isinstance(archive, bool) and archive is not None:
        archive = str(archive).lower()
    else:
        archive = 'true'
    if isinstance(distributor, bool):
        distributor = 'true'
    else:
        distributor = 'true'
    HEADER['command'] = cmd % (create_table, update_tsd_info, archive, distributor, master_node)

    if 'Not declared' in get_cmd.get_processes(conn=conn, exception=exception).split('Operator')[-1].split('\r')[0]:
        r, error = conn.post(command=cmd)
        if errors.print_error(conn=conn.conn, request_type='post', command=cmd, r=r, error=error, exception=exception) is True:
            status = False

        for cmd in ['run streamer', 'run data distributor', 'run data consumer where start_date=-30d']:
            HEADER['command'] = cmd
            r, error = conn.post(headrs=HEADER)
            if errors.print_error(conn=conn.conn, request_type='post', command=cmd, r=r, error=error, exception=exception) is True:
                status = False

    return status


def set_immediate_threshold(conn:anylog_api.AnyLogConnect, exception:bool=False)->bool:
    """
    Set threshold to immidiate
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
    HEADER['command'] = "set buffer threshold where write_immediate = true"

    r, error = conn.post(headers=HEADER)
    if errors.print_error(conn=conn.conn, request_type='post', command=cmd, r=r, error=error, exception=exception) is True:
        status = False 

    return status 


def run_mqtt(conn:anylog_api.AnyLogConnect, config:dict, exception:bool=False)->bool: 
    """
    Connect to MQTT
    :link:
        https://github.com/AnyLog-co/documentation/blob/master/mqtt.md
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
    :return:
        bool
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
        cmd = execute_cmd % (config['mqtt_topic_name'], config['mqtt_topic_dbms'], config['mqtt_topic_table'],
                     config['mqtt_column_timestamp'], config['mqtt_column_value_type'], config['mqtt_column_value'])
    HEADER['command'] = cmd
    r, error = conn.post(headers=HEAD)
    if errors.print_error(conn=conn.conn, request_type="post", command=cmd, r=r, error=error, exception=exception):
        status = False

    """
    # Bug with function
    if config['enable_other_mqtt'] == 'true' and status is not False and config['mqtt_topic_name'] != '#':
        execute_cmd = cmd + ' and topic="#"'
        r, error = conn.post(command=execute_cmd)
        if errors.post_error(conn=conn.execute_cmd, command=cmd, r=r, error=error, exception=exception) is True:
            status = False
    """
    
    return status