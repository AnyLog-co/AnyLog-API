import time

import __init__
import post_cmd
import anylog_api
import blockchain_cmd
import dbms_cmd
import policy_cmd


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

    # default dbms
    if config['default_dbms'] not in dbms_list:
        if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name=config['default_dbms'], exception=exception):
            print('Failed to start %s database' % config['default_dbms'])

    # declare cluster & operator in blockchain
    deploy_operator = 'y'
    if 'enable_cluster' in config and config['enable_cluster'].lower() == 'true':
        cluster_id = policy_cmd.declare_anylog_policy(conn=conn, policy_type='cluster', config=config,
                                                      master_node=config['master_node'], location=location,
                                                      exception=exception)
        if cluster_id is not None:
            config['cluster_id'] = cluster_id
        else:
            boolean = False
            while boolean is False:
                deploy_operator = input('Failed to get cluster ID. Would you still like to set an operator (y/n)? ')
                deploy_operator = deploy_operator.lower()
                if deploy_operator not in ['y', 'n']:
                    deploy_operator = input('Invalid option: %s. Would you still like to set an operator (y/n)? ')
                else:
                    boolean = True
    if deploy_operator == 'y':
        node_id = policy_cmd.declare_anylog_policy(conn=conn, policy_type=config['node_type'], config=config,
                                                      master_node=config['master_node'], location=location,
                                                      exception=exception)
        if node_id is None:
            rint('Failed to add % node to blockchain' % config['node_typp'])
    else:
        print("Notice: Operator node was not added to the blockchain as a corresponding cluster ID wasn't found.")

    # Partition
    if 'enable_partition' in config and config['enable_partition'].lower() == 'true':
        tables = ['*']
        if 'table' in config:
            tables = config['table'].split(',')
        for table in tables:
            # create partition
            if not dbms_cmd.declare_db_partitions(conn=conn, db_name=config['default_dbms'], table_name=table,
                                           ts_column=config['partition_column'], interval=config['partition_interval'],
                                           exception=exception):
                print('Failed to declare partition for %s.%s' % (config['default_dbms'], table))
            # validate partition exists
            if not dbms_cmd.get_partitions(conn=conn, db_name=config['default_dbms'], table_name='*'):
                print('Failed to declare partition for %s.%s' % (config['default_dbms'], table))

    # MQTT
    if 'enable_mqtt' in config and config['enable_mqtt'] == 'true':
        if not post_cmd.run_mqtt(conn=conn, config=config, exception=exception):
            print('Failed to start MQTT client')

    if not post_cmd.set_immediate_threshold(conn=conn, exception=exception):
        print('Failed to set data streaming to immediate')

    # Start operator
    if not post_cmd.run_operator(conn=conn, master_node=config['master_node'], create_table=True,
                                      update_tsd_info=True, archive=True, distributor=True, exception=False):
        print('Failed to set buffering to start publisher')