import __init__
import declare_node
import rest.anylog_api as anylog_api
import rest.blockchain_cmd as blockchain_cmd
import rest.dbms_cmd as dbms_cmd
import rest.post_cmd

def operator_init(conn:anylog_api.AnyLogConnect, config:dict, location:bool=True, exception:bool=False):
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
        blockchain:dict - conetent from blockchain
        new_policy:dict - decleration of policy
    """
    status = True

    # Create system_query & blockchain
    new_system = False
    dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
    if dbms_list == 'No DBMS connections found':
        new_system = True
    if new_system == True or 'system_query' not in dbms_list:
        if not dbms_cmd.connect_dbms(conn=conn, config={}, db_name='system_query', exception=exception):
            print('Failed to start system_query database')

    if new_system == True or 'almgm' not in dbms_list:
        if not dbms_cmd.connect_dbms(conn=conn, config={}, db_name='almgm', exception=exception):
            print('Failed to start system_query database')

    # create tsd_info for almgm
    if not dbms_cmd.check_table(conn=conn, db_name='almgm', table_name='tsd_info', exception=exception):
        if not dbms_cmd.create_table(conn=conn, db_name='almgm', table_name='tsd_info', exception=exception):
            print('Failed to create almgm.tsd_info table')

    if 'default_dbms' in config:
        if new_system == True or config['default_dbms'] not in dbms_list:
            if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name='system_query', exception=exception):
                print('Failed to start %s database' % config['default_dbms'])

    if 'enable_mqtt' in config and config['enable_mqtt'] == 'true':
        if not rest.post_cmd.run_mqtt(conn=conn, config=config, exception=exception):
            print('Failed to start MQTT client')

    if not rest.post_cmd.run_operator(conn=conn, master_node=config['master_node'], create_table=True, update_tsd_info=True, archive=True, distributor=True, exception=exception):
        print('Failded to start operator')

    # blockchain sync
    status = blockchain_cmd.blockchain_sync(conn=conn, source='master', time='1 minute', connection=config['master_node'], exception=exception)
    if status == False:
        print('Failed to set blockchain sync process')

    # Post scheduler 1
    if not rest.post_cmd.start_scheduler1(conn=conn, exception=exception):
        print('Failed to start scheduler 1')
