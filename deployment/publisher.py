import __init__
import post_cmd
import anylog_api
import blockchain_cmd
import dbms_cmd
import create_declaration
import execute_anylog_file



def publisher_init(conn:anylog_api.AnyLogConnect, config:dict, location:bool=True, exception:bool=False): 
    """
    Deploy a query or publisher node instance via REST 
    :definition: 
        Nodes that simply generate data and send them to operator nodes
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
        if not dbms_cmd.connect_dbms(conn=conn, config={}, db_name='system_query', exception=exception):
            print('Failed to start system_query database')
    # almgm & tsd_info
    if new_system is True or 'almgm' not in dbms_list:
        if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name='almgm', exception=exception):
            print('Failed to start almgm database')
    if new_system is True or dbms_cmd.get_table(conn=conn, db_name='almgm', table_name='tsd_info',
                                                      exception=exception) is False:
        if not dbms_cmd.create_table(conn=conn, db_name='almgm', table_name='tsd_info', exception=exception):
            print('Failed to create table almgm.tsd_info')

    # Pull blockchain & declare node if not exists
    if not declare_policy_cmd.declare_node(conn=conn, config=config, location=location, exception=exception):
        print('Failed to declare publisher node on blockchain')

    if 'enable_mqtt' in config and config['enable_mqtt'] == 'true':
        if not post_cmd.run_mqtt(conn=conn, config=config, exception=exception):
            print('Failed to start MQTT client')

    if not post_cmd.set_immediate_threshold(conn=conn, exception=exception):
        print('Failed to set data streaming to immediate')

    # Start publisher
    if not post_cmd.run_publisher(conn=conn, master_node=config['master_node'], dbms_name='file_name[0]', table_name='file_name[1]', compress_json=True, move_json=True, exception=exception):
        print('Failed to set buffering to start publisher')


