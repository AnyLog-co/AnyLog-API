import os
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).rsplit('deployment', 1)[0]
rest_dir = os.path.join(ROOT_PATH, 'rest')
support_dir = os.path.join(ROOT_PATH, 'support')
sys.path.insert(0, rest_dir)
sys.path.insert(0, support_dir)

import anylog_api
import blockchain_cmd
import get_cmd
import post_cmd
import dbms_cmd

def deplog_genric_params(conn:anylog_api.AnyLogConnect, env_configs:dict, exception:bool=False)->bool:
    """
    Configurations params required by all nodes
        * run scheduler
        * blockchain sync
        * connect to database(s)
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        env_configs:dict - environment configuration
        exception:bool - whether to print exceptions
    :params:
        error_msgs:list - when a process fails, the corresponding notification
        error:str - generic error messae
        dbms_list;list - list of connected database(s) if any
    """
    error_msgs = []

    # set scheduler
    if not post_cmd.start_exitings_scheduler(conn=conn, scheduler_id=1, exception=exception):
        error_msgs.append('Failed to start default scheduler 1')

    try:
        sync_time = env_configs['blockchain_sync']['sync_time']
    except:
        sync_time = '30 second'

    # run blockchain sync
    if not blockchain_cmd.blockchain_sync_scheduler(conn=conn, source='master', time=sync_time,
                                                    master_node=env_configs['networking']['master_node'],
                                                    exception=exception):
        error_msgs.append('Failed to set automated blockchain sync process')

    # declare databases
    error = "Failed to connect to database of type: '%s'"
    dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)

    if 'system_query' not in dbms_list and not dbms_cmd.connect_dbms(conn=conn,
                                                                      db_type=env_configs['database']['db_type'],
                                                                      db_credentials=env_configs['database']['db_user'],
                                                                      db_port=env_configs['database']['db_port'],
                                                                      db_name='system_query', exception=exception):
        error_msgs.append(error % 'system_query')

    if env_configs['general']['node_type'] in ['master', 'single-node', 'single-node-publisher']:
        if 'blockchain' not in dbms_list and not dbms_cmd.connect_dbms(conn=conn,
                                                                        db_type=env_configs['database']['db_type'],
                                                                        db_credentials=env_configs['database']['db_user'],
                                                                        db_port=env_configs['database']['db_port'],
                                                                        db_name='blockchain', exception=exception):
            error_msgs.append(error % 'blockchain') 

    if env_configs['general']['node_type'] not in ['master', 'query']:
        if 'almgm' not in dbms_list and not dbms_cmd.connect_dbms(conn=conn,
                                                                        db_type=env_configs['database']['db_type'],
                                                                        db_credentials=env_configs['database']['db_user'],
                                                                        db_port=env_configs['database']['db_port'],
                                                                        db_name='almgm', exception=exception):
            error_msgs.append(error % 'almgm')

        elif not dbms_cmd.get_table(conn=conn, db_name='almgm', table_name='tsd_info', exception=exception):
            if not dbms_cmd.create_table(conn=conn, db_name='almgm', table_name='tsd_info', exception=exception):
                error_msgs.append("Faileed to create table 'almgm.tsd_info'")

    if env_configs['general']['node_type'] in ['operator', 'single-node']:
        try:
            default_dbms = env_configs['database']['default_dbms']
        except:
            error_msgs.append('Missing logical database for operator nodee')
        else:
            if default_dbms not in dbms_list and not dbms_cmd.connect_dbms(conn=conn,
                                                                            db_type=env_configs['database']['db_type'],
                                                                            db_credentials=env_configs['database']['db_user'],
                                                                            db_port=env_configs['database']['db_port'],
                                                                            db_name='almgm', exception=exception):
                error_msgs.append(error % default_dbms)


    print(error_msgs) 
