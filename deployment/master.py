import os 
import sys 

import declare_node 

rest_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/rest')) 
sys.path.insert(0, rest_dir) 

import blockchain_cmd 
import dbms_cmd
import rest 

def master_init(conn:str, config_data:dict): 
    """
    Sample config: 
    {'anylog_root_dir': '/app', 'build_type': 'local', 'node_type': 'master', 'node_name': 'master', 'company_name': 'anylog', 'master_node': '10.0.0.42:2048', 'anylog_server_port': 2048, 'anylog_rest_port': 2049, 'db_type': 'sqlite', 'db_user': 'anylog@127.0.0.1:demo', 'db_port': 5432}
    """
    # connect DBMS & create ledger if not exists 
    status = dbms_cmd.connect_dbms(conn=conn, config=config_data, db_name='blockchain', auth=None, timeout=30) 
    if status == False: 
        print('Failed to declare blockchain datbase on node') 
    else: 
        if dbms_cmd.check_table(conn:str, db_name='blockchain', table_name='ledger', auth=None, timeout=timeout) == False: 
            status = dbms_cmd.create_table(conn=conn, db_name='blockchain', table_name='ledger', auth=None, timeout=30)
            if status == False: 
                print('Failed to create table table ledger') 

    # if config == {} then it wlll connect via SQLite 
    status = dbms_cmd.connect_dbms(conn=conn, config={}, db_name='system_query', auth=None, timeout=30) 
    if status == False: 
        print('Failed to declare system_query database on node') 

    # declare node if not in blockchain
    blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type='master', where:list=['ip=%s' % config['external_ip']], auth=None, timeout=30)
    if blocckchain == []: 
        node = declare_node.declare_node(config=config_data)
        if rest.post_policy(conn=conn, policy=node, master_node=config['master_node'], auth=None, timeout=30) == False: 
            print('Failed to declare node on %s' % config['master_node'] 


