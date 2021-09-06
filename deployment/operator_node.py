import time

import rest.post_cmd
import rest.anylog_api as anylog_api
import rest.blockchain_cmd as blockchain_cmd
import rest.dbms_cmd as dbms_cmd
import support.create_declaration as create_declaration


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
    if new_system is True or rest.dbms_cmd.get_table(conn=conn, db_name='almgm', table_name='tsd_info',
                                                      exception=exception) is False:
        if not dbms_cmd.create_table(conn=conn, db_name='almgm', table_name='tsd_info', exception=False):
            print('Failed to create table almgm.tsd_info')
    # default dbms
    if new_system is True or config['default_dbms'] not in dbms_list:
        if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name=config['default_dbms'], exception=exception):
            print('Failed to start %s database' % config['default_dbms'])

    # Pull blockchain & declare cluster if not exists
    if 'enable_cluster' in config and config['enable_cluster'].lower() == 'true':
        if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception=exception):
            blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type='cluster',
                                                       where=['company=%s' % config['company_name'],
                                                              'name=%s' % config['cluster_name']],
                                                       exception=exception)
            if len(blockchain) == 0:
                new_policy = create_declaration.declare_cluster(config=config)
                post_policy = blockchain_cmd.post_policy(conn=conn, policy=new_policy,
                                                         master_node=config['master_node'], exception=exception)
            elif len(blockchain) > 0 and 'id' in blockchain[0]['cluster']:
                config['cluster_id'] = blockchain[0]['cluster']['id']
            else:
                print('Failed to extract cluster id')
        else:
           print('Failed to check/create if cluster exists')

        if post_policy is False and len(blockchain) == 0 and blockchain_cmd.pull_json(conn=conn,
                                                                                      master_node=config['master_node'],
                                                                                      exception=exception):
            blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type='cluster',
                                                       where=['company=%s' % config['company_name'],
                                                              'name=%s' % config['cluster_name']],
                                                       exception=exception)
            if len(blockchain) > 0 and 'id' in blockchain[0]['cluster']:
                config['cluster_id'] = blockchain[0]['cluster']['id']
            else:
                print('Failed to extract cluster id')
        else:
            print('Failed to extract cluster id')

    # Pull blockchain & declare operator if not exists
    if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception=exception):
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

    # Partition
    if 'enable_partition' in config and config['enable_partition'].lower() == 'true':
        tables = ['*']
        if 'table' in config:
            tables = config['table'].split(',')
        for table in tables:
            # create partition
            if not dbms_cmd.declare_db_partitions(conn=conn, db_name=config['default_dbms'], table_name=table,
                                           ts_column=config['partition_column'], interval=config['partition_interval'],
                                           exception=False):
                print('Failed to declare partition for %s.%s' % (config['default_dbms'], table))
            # validate partition exists
            #if not dbms_cmd.get_partitions(conn=conn, db_name=config['default_dbms'], table_name='*'):
            #    print('Failed to declare partition for %s.%s' % (config['default_dbms'], table))

    # MQTT
    if 'enable_mqtt' in config and config['enable_mqtt'] == 'true':
        if not rest.post_cmd.run_mqtt(conn=conn, config=config, exception=exception):
            print('Failed to start MQTT client')

    # blockchain sync
    if not blockchain_cmd.blockchain_sync(conn=conn, source='master', time='1 minute', connection=config['master_node'], exception=exception):
        print('Failed to set blockchain sync process')

    # Post scheduler 1
    if not rest.post_cmd.start_scheduler1(conn=conn, exception=exception):
        print('Failed to start scheduler 1')

    # Start operator
    if not rest.post_cmd.run_operator(conn=conn, master_node=config['master_node'], create_table=True,
                                      update_tsd_info=True, archive=True, distributor=True, exception=False):
        print('Failed to set buffering to start publisher')

    if not rest.post_cmd.set_immidiate_threshold(conn=conn, exception=exception):
        print('Failed to set data streaming to immediate')

