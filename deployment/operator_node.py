import __init__
import declare_cluster
import declare_node
import rest.anylog_api as anylog_api
import rest.blockchain_cmd as blockchain_cmd
import rest.dbms_cmd as dbms_cmd
import rest.post_cmd

def __get_cluster(conn:anylog_api.AnyLogConnect, config:dict, exception:bool=False)->list:
    """
    blockchain get cluuster
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        config:dict - configuration
        exception:bool - whether to print execption
    :param:
        cluster:list - cluster from blockchain
    :return:
        cluster
    """
    cluster = {}
    if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception=exception):
        if 'cluster_name' in config and 'company_name' in config:
            clusters = blockchain_cmd.blockchain_get(conn=conn, policy_type=config['node_type'],
                                                 where=['name=%s' % config['cluster_name'],
                                                        'company=%s' % config['company_name']],
                                                 exception=exception)
        elif 'cluster_id' in config:
            clusters = blockchain_cmd.blockchain_get(conn=conn, policy_type=config['node_type'],
                                                 where=['id=%s' % config['cluster_id']],
                                                 exception=exception)
        elif 'cluster_name' in config and 'company_name' in config:
            clusters = blockchain_cmd.blockchain_get(conn=conn, policy_type=config['node_type'],
                                                 where=['name=%s' % config['cluster_name']], exception=exception)
    return clusters

def __declare_operator(conn:anylog_api.AnyLogConnect, config:dict, exception:bool=False)->bool:
    """
    Declare Operator (and cluster) node process
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        config:dict - configuration
        exception:bool - whether to print execption
    :steps:
        if operator exists DNE
            1. check if cluster exists
            2. if not create cluster
            3. extract cluster ID
            4. create operator
    """
    if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception=exception):
        data = blockchain_cmd.blockchain_get(conn=conn, policy_type=config['node_type'],
                                             where=['ip=%s' % config['external_ip'],
                                                    'port=%s' % config['anylog_tcp_port']], exception=exception)
        if len(data) == 0:
            if 'master_node' in config and 'enable_cluster' in config and str(config['enable_cluster']).lower() == 'true':
                """
                check cluster 
                    if not create cluster
                extract cluster ID
                """
                clusters = __get_cluster(conn=conn, config=config, exception=exception)
                if len(clusters) == 0:
                    cluster = declare_cluster.declare_cluster(config=config)
                    if not blockchain_cmd.post_policy(conn=conn, policy=cluster, master_node=config['master_node'], exception=exception):
                        clusters = __get_cluster(conn=conn, config=config, exception=exception)
                for cluster in clusters:
                    print(cluster)
            # declare operator










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

    __declare_operator(conn=conn, config=config, exception=exception)
    exit(1)
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
