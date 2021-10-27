import __init__
import anylog_api
import dbms_cmd
import monitoring_cmd
import policy_cmd
import post_cmd

def single_node_init(conn:anylog_api.AnyLogConnect, config:dict, node_types:list, disable_location:bool=False, exception:bool=False):
    """
    Deploy multiple types of AnyLog instances on a single (docker) container
    :deployment: 
        * node type: master
            - blockchain & ledger 
            - add policy to blockchain
        * node type: query
            - system_query based on db info
        * node type: publisher OR operator
            - almgm & tsd_info
            - if operator, create database
            - add policy to blockchain
            - start corresponding process
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        config:dict - configuration information
        node_types:list - types of nodes to deploy
        location:bool - whether to add location in policy
        exception:bool - whether to print exception
    """
    if 'operator' in node_types and 'publisher' in node_types:
        node = input("A 'solo deployment' can only have either operator or publisher process on a given container. Would you like operator or publisher? ")
        while node.lower() not in ['operator', 'publisher']:
            node = input('Invalid option: %s. Would you like to run an operator or publisher process? ')
        if node == 'publisher':
            node_types.remove('operator')
        else:
            node_types.remove('publisher')

    for node in node_types:
        config['node_type'] = node
        if node == 'master':
            dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
            if 'blockchain' not in dbms_list:
                if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name='blockchain', exception=exception):
                    print('Failed to start blockchain database')
            # Create table ledger 
            if not dbms_cmd.get_table(conn=conn, db_name='blockchain', table_name='ledger', exception=exception):
                # Create ledger if not exists
                if not dbms_cmd.create_table(conn=conn, db_name='blockchain', table_name='ledger', exception=exception):
                    print('Failed to create table blockchain.ledger')

            node_id = policy_cmd.declare_anylog_policy(conn=conn, policy_type=node, config=config,
                                                   master_node='local', disable_location=disable_location, exception=exception)
            if node_id is None:
                print('Failed to add %s node to blockchain' % node)
        elif node == 'query':
            if 'system_query' not in dbms_list:
                if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name='system_query', exception=exception):
                    print('Failed to start system_query database')
        elif node in ['publisher', 'operator']:
            # Setup almgm databse & tsd_info table
            dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
            if 'almgm' not in dbms_list:
                if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name='almgm', exception=exception):
                    print('Failed to start almgm database')
            dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
            if 'almgm' in dbms_list and not dbms_cmd.get_table(conn=conn, db_name='almgm', table_name='tsd_info',
                                                               exception=exception):
                if not dbms_cmd.create_table(conn=conn, db_name='almgm', table_name='tsd_info', exception=exception):
                    print('Failed to create table almgm.tsd_info')

            # Start MQTT
            if 'enable_mqtt' in config and config['enable_mqtt'] == 'true':
                if not post_cmd.run_mqtt(conn=conn, config=config, exception=exception):
                    print('Failed to start MQTT client')
            # Set threshold
            if not post_cmd.set_immediate_threshold(conn=conn, exception=exception):
                print('Failed to set data streaming to immediate')

            if node == 'operator':
                # connect to default DBMS
                dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
                if config['default_dbms'] not in dbms_list:
                    if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name=config['default_dbms'],
                                                 exception=exception):
                        print('Failed to start %s database' % config['default_dbms'])

                # declare cluster & operator in blockchain
                deploy_operator = 'y'
                if 'enable_cluster' in config and config['enable_cluster'].lower() == 'true':
                    cluster_id = policy_cmd.declare_anylog_policy(conn=conn, policy_type='cluster', config=config,
                                                                  master_node='local', location=location,
                                                                  exception=exception)
                    if cluster_id is not None:
                        config['cluster_id'] = cluster_id
                    else:
                        deploy_operator = None
                        while deploy_operator not in ['y', 'n']:
                            if deploy_operator is None:
                                try:
                                    deploy_operator = input('Failed to get cluster ID. Would you still like to declare an operator (y/n)? ')
                                except EOFError:
                                    deploy_operator = 'y'
                            else:
                                try:
                                    deploy_operator = input('Invalid Option: %s.  Would you still like to declare an operator (y/n)? ' % deploy_operator)
                                except EOFError:
                                    deploy_operator = 'y'

                if deploy_operator == 'y':
                    node_id = policy_cmd.declare_anylog_policy(conn=conn, policy_type=config['node_type'],
                                                               config=config, master_node='local',
                                                               location=location, exception=exception)
                    if node_id is None:
                        print('Failed to add %s node to blockchain' % node)
                else:
                    print("Notice: Operator node was not added to the blockchain as a corresponding cluster ID wasn't found.")

                # Partition
                if 'enable_partition' in config and config['enable_partition'].lower() == 'true':
                    tables = ['*']
                    if 'table' in config:
                        tables = config['table'].split(',')
                    for table in tables:
                        # create partition
                        if not dbms_cmd.declare_db_partitions(conn=conn, db_name=config['default_dbms'],
                                                              table_name=table,
                                                              ts_column=config['partition_column'],
                                                              interval=config['partition_interval'],
                                                              exception=exception):
                            print('Failed to declare partition for %s.%s' % (config['default_dbms'], table))
                        # validate partition exists
                        if not dbms_cmd.get_partitions(conn=conn, db_name=config['default_dbms'], table_name='*'):
                            print('Failed to declare partition for %s.%s' % (config['default_dbms'], table))

                    # by default we are dropping partitions that are older than 60 days (~2 months).
                    if not dbms_cmd.drop_partitions(conn=conn, db_name=config['default_dbms'],
                                                    partition_name=None, table_name='*',
                                                    keep=60, scheduled=True, exception=exception):
                        print('Failed to set a scheduled process to drop partitions')

                if not monitoring_cmd.set_monitor_streaming_data(conn=conn, db_name=config['default_dbms'],
                                                                 table_name='*', intervals=10, frequency='1 minute',
                                                                 value_col='value', exception=exception):
                    print('Failed to set monitoring for streaming data')

                '''
                # Issue 256
                """
                If an operator is an associated with a cluster that has tables then the code doesn't allow adding new 
                tables to be added into the cluster 
                """
                create_table = True
                if 'enable_cluster' in config and config['enable_cluster'] == 'true' and 'table' in config:
                    create_table = False
                '''

                # Start operator
                if not post_cmd.run_operator(conn=conn, master_node=config['master_node'], create_table=True,
                                             update_tsd_info=True, archive=True, distributor=True, exception=False):
                    print('Failed to set buffering to start operator')

            elif node == 'publisher':
                node_id = policy_cmd.declare_anylog_policy(conn=conn, policy_type=config['node_type'], config=config,
                                                           master_node='local', location=location,
                                                           exception=exception)
                if node_id is None:
                    print('Failed to add % node to blockchain' % node)

                # Start publisher
                if not post_cmd.run_publisher(conn=conn, master_node=config['master_node'], dbms_name='file_name[0]',
                                              table_name='file_name[1]', compress_json=True, move_json=True,
                                              exception=exception):
                    print('Failed to set buffering to start publisher')





