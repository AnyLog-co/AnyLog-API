import __init__
import post_cmd
import anylog_api
import blockchain_cmd
import dbms_cmd
import create_declaration
import execute_anylog_file


def query_init(conn:anylog_api.AnyLogConnect, config:dict, location:bool=True, exception:bool=False): 
    """
    Deploy a query node instance via REST 
    :definition: 
        Nodes dedicated to query and BI activity
    :args:
       anylog_conn:anylog_api.AnyLogConnect - Connection to AnyLog 
       config:dict - config data (from file + hostname + AnyLog) 
       location:bool -whetther or not to have location in policy
       exception:bool - whether or not to print exception to screen 
    :params: 
        status:bool 
        new_system:bool - variable to check whether we are dealing with a new setup or not
        blockchain:dict - content from blockchain
        new_policy:dict - declaration of policy
    """
    # Create system_query & blockchain 
    new_system = False
    dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
    if dbms_list == 'No DBMS connections found': 
        new_system = True
    if new_system is True or 'system_query' not in dbms_list:
        if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name='system_query', exception=exception):
            print('Failed to start system_query database') 

    # Pull blockchain & declare node if not exists
    if not declare_policy_cmd.declare_node(conn=conn, config=config, location=location, exception=exception):
        print('Failed to declare query node on blockchain')

