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
        if not dbms_cmd.create_table(conn=conn, db_name='almgm', table_name='tsd_info', exception=False):
            print('Failed to create table almgm.tsd_info')

    # Pull blockchain & declare node if not exists
    if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception =exception):
        blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=config['node_type'],
                                                   where=['ip=%s' % config['external_ip'],
                                                          'port=%s' % config['anylog_tcp_port']],
                                                   exception=exception)
        if len(blockchain) == 0:
            new_policy = create_declaration.declare_node(config=config, location=location)
            post_policy = blockchain_cmd.post_policy(conn=conn, policy=new_policy, master_node=config['master_node'],
                                                     exception=exception)

        if len(blockchain) == 0 and blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'],
                                                             exception=exception):
            blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=config['node_type'],
                                                       where=['ip=%s' % config['external_ip'],
                                                              'port=%s' % config['anylog_tcp_port']],
                                                       exception=exception)
            if len(blockchain) == 0:
                print('Failed to declare policy')

    if 'enable_mqtt' in config and config['enable_mqtt'] == 'true':
        if not post_cmd.run_mqtt(conn=conn, config=config, exception=exception):
            print('Failed to start MQTT client')

    # execute AnyLog file
    if 'execute_file' in config and config['execute_file'] == 'true':
        if 'anylog_file' in config:
            if not execute_anylog_file.execute_file(conn=conn, anylog_file=config['anylog_file'], exception=exception):
                print('Failed to execute AnyLog file: %s' % config['anylog_file'])

    # blockchain sync 
    if not blockchain_cmd.blockchain_sync(conn=conn, source='master', time='1 minute', connection=config['master_node'], exception=exception):
        print('Failed to set blockchain sync process')

    # Post scheduler 1
    if not post_cmd.start_scheduler1(conn=conn, exception=exception):
        print('Failed to start scheduler 1')

    # Start publisher
    if not post_cmd.run_publisher(conn=conn, master_node=config['master_node'], dbms_name='file_name[0]', table_name='file_name[1]', compress_json=True, move_json=True, exception=exception):
        print('Failed to set buffering to start publisher')

    if not post_cmd.set_immediate_threshold(conn=conn, exception=exception):
        print('Failed to set data streaming to immediate')


