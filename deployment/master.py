import os 
import sys 

import declare_node 

rest_dir   = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/rest')) 
sys.path.insert(0, rest_dir) 

import blockchain_cmd 
import dbms_cmd
import rest 

def master_init(conn:rest.AnyLogConnect, config_data:dict): 
    """
    Deploy a master node instance via REST 
    :definition: 
        A "notary" system between other nodes in the network via either a public or private blockchain
    :args:
       anylog_conn:rest.AnyLogConnect - Connection to AnyLog 
       config:dict - config data (from file + hostname + AnyLog) 
    :params: 
        status:bool 
    """
    # Create databases 
    status = dbms_cmd.connect_dbms(conn=conn, config=config_data, db_name='blockchain', auth=None, timeout=30) 
