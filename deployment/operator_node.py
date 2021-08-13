import __init__
import declare_cluster
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

    # declare cluster
    if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception=exception):
        if 'enable_cluster' in config and config['enable_cluster'] == 'true':
            if 'cluster_name' in config:
                blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type='cluster', where=['name=%s' % config['cluster_name']], exception=exception)
                if len(blockchain) == 0: # if not found, declare cluster
                    new_cluster = declare_cluster.declare_cluster(config=config)
                    blockchain_cmd.post_policy(conn=conn, policy=new_cluster, master_node=config['master_node'], exception=exception)

    # declare operator
    if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception=exception):
        if 'enable_cluster' in config and config['enable_cluster'] == 'true':
            if 'cluster_name' in config:
                blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type='cluster', where=['name=%s' % config['cluster_name']], exception=exception)
                for cluster in blockchain:
                    if 'parent' not in cluster['cluster']:
        new_node = declare_node.declare_node(config=config, location=True)
                        config['cluster_id'] = cluster['cluster']['id']
        new_node = declare_node.declare_operator(node=new_node, config=config)
        blockchain_cmd.post_policy(conn=conn, policy=new_node, master_node=config['master_node'], exception=exception)

    if 'enable_mqtt' in config and config['enable_mqtt'] == 'true':
        if not rest.post_cmd.run_mqtt(conn=conn, config=config, exception=exception):
            print('Failed to start MQTT client')

    if not dbms_cmd.declare_db_partitions(conn=conn, db_name=config['default_dbms'], table_name='*', ts_column='timestamp', value=1, interval='day', exception=False):
        print('Failed to set partitions to %s.%s' % (config['default_dbms'], '*'))

    if not rest.post_cmd.run_operator(conn=conn, master_node=config['master_node'], create_table=True, update_tsd_info=True, archive=True, distributor=True, exception=exception):
        print('Failed to start operator')

    if not rest.post_cmd.set_immidiate_threshold(conn=conn, exception=exception):
        print('Failed to set data streaming to immediate')

    # blockchain sync
    if not blockchain_cmd.blockchain_sync(conn=conn, source='master', time='1 minute', connection=config['master_node'], exception=exception):
        print('Failed to set blockchain sync process')

    # Post scheduler 1
    if not rest.post_cmd.start_scheduler1(conn=conn, exception=exception):
        print('Failed to start scheduler 1')
