import __init__
import anylog_api
import blockchain_cmd
import dbms_cmd
import post_cmd
import declare_policy_cmd


def master_init(conn:anylog_api.AnyLogConnect, config:dict, location:bool=True, exception:bool=False): 
    """
    Deploy a master node instance via REST 
    :definition: 
        A "notary" system between other nodes in the network via either a public or private blockchain
    :args:
       anylog_conn:anylog_api.AnyLogConnect - Connection to AnyLog 
       location:bool -whetther or not to have location in policy
       config:dict - config data (from file + hostname + AnyLog) 
       exception:bool - whether or not to print exception to screen 
    :params: 
        status:bool 
        new_system:bool - variable to check whether we are dealing with a new setup or not
        blockchain:dict - conetent from blockchain
        new_policy:dict - decleration of policy
    """
    # Create system_query & blockchain 
    new_system = False
    dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
    if dbms_list == 'No DBMS connections found': 
        new_system = True
    if new_system is True or 'system_query' not in dbms_list:
        if not dbms_cmd.connect_dbms(conn=conn, config={}, db_name='system_query', exception=exception):
            print('Failed to start system_query database') 
    if new_system is True or 'blockchain' not in dbms_list:
        if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name='blockchain', exception=exception):
            print('Failed to start blockchain database') 

    # Create table ledger
    if not dbms_cmd.get_table(conn=conn, db_name='blockchain', table_name='ledger', exception=exception):
        # Create ledger if not exists 
        if not dbms_cmd.create_table(conn=conn, db_name='blockchain', table_name='ledger', exception=exception):
            print('Failed to create table blockchain.ledger') 

    if not declare_policy_cmd.declare_node(conn=conn, config=config, location=location, exception=exception):
        print('Failed to declare master node on blockchain')