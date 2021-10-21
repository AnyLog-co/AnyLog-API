import __init__
import anylog_api
import dbms_cmd
import policy_cmd
import post_cmd

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
    dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
    # almgm & tsd_info
    if 'almgm' not in dbms_list:
        if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name='almgm', exception=exception):
            print('Failed to start almgm database')

    dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
    if 'almgm' in dbms_list and not dbms_cmd.get_table(conn=conn, db_name='almgm', table_name='tsd_info', exception=exception):
        if not dbms_cmd.create_table(conn=conn, db_name='almgm', table_name='tsd_info', exception=exception):
            print('Failed to create table almgm.tsd_info')

    # declare Publisher
    node_id = policy_cmd.declare_anylog_policy(conn=conn, policy_type=config['node_type'], config=config,
                                               master_node=config['master_node'], location=location, exception=exception)
    if node_id is None:
        print('Failed to add % node to blockchain' % config['node_typp'])

    if 'enable_mqtt' in config and config['enable_mqtt'] == 'true':
        if not post_cmd.run_mqtt(conn=conn, config=config, exception=exception):
            print('Failed to start MQTT client')

    if not post_cmd.set_immediate_threshold(conn=conn, exception=exception):
        print('Failed to set data streaming to immediate')

    # Start publisher
    if not post_cmd.run_publisher(conn=conn, master_node=config['master_node'], dbms_name='file_name[0]',
                                  table_name='file_name[1]', compress_json=True, move_json=True, exception=exception):
        print('Failed to set buffering to start publisher')


