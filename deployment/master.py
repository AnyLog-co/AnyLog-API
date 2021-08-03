import os 
import sys 


rest_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/rest')) 
sys.path.insert(0, rest_dir) 

import rest 

def master_init(conn:str, config_data:dict): 
    """
    Sample config: 
    {'anylog_root_dir': '/app', 'build_type': 'local', 'node_type': 'master', 'node_name': 'master', 'company_name': 'anylog', 'master_node': '10.0.0.42:2048', 'anylog_server_port': 2048, 'anylog_rest_port': 2049, 'db_type': 'sqlite', 'db_user': 'anylog@127.0.0.1:demo', 'db_port': 5432}
    """
    # connect DBMS 
    cmd = "connect dbms %s %s %s blockchain" % (config_data['db_type'],  config_data['db_user'], config_data['db_port'])
    status = rest.post(conn=conn, command=cmd)
    if status == False: 
        print('Failed to declare blockchain datbase on node') 

    cmd = "connect dbms sqlite %s %s system_query" % (config_data['db_user'], config_data['db_port'])
    status = rest.post(conn=conn, command=cmd)
    if status == False: 
        print('Failed to declare system_query database on node') 

    # Declare policy 


