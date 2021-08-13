import __init__
import declare_node
import rest.anylog_api as anylog_api
import rest.blockchain_cmd as blockchain_cmd
import rest.dbms_cmd as dbms_cmd
import rest.post_cmd

def master_init(conn:anylog_api.AnyLogConnect, config:dict, location:bool=True, exception:bool=False): 
    """
    Deploy a master node instance via REST 
    :definition: 
        A "notary" system between other nodes in the network via either a public or private blockchain
    :args:
       anylog_conn:anylog_api.AnyLogConnect - Connection to AnyLog 
       location:bool -whetther or not to have location in policy
       config:dict - config data (from file + hostname + AnyLog) 
       exception:bool - whether or not to print exception to screen 
    :params: 
        status:bool 
        new_system:bool - variable to check whether we are dealing with a new setup or not
        blockchain:dict - conetent from blockchain
        new_policy:dict - decleration of policy
    """
    # Create system_query & blockchain 
    new_system = False
    dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
    if dbms_list == 'No DBMS connections found': 
        new_system = True
    if new_system is True or 'system_query' not in dbms_list:
        if not dbms_cmd.connect_dbms(conn=conn, config={}, db_name='system_query', exception=exception):
            print('Failed to start system_query database') 
    if new_system is True or 'blockchain' not in dbms_list:
        if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name='blockchain', exception=exception):
            print('Failed to start blockchain database') 

    # Create table ledger
    if not dbms_cmd.check_table(conn=conn, db_name='blockchain', table_name='ledger', exception=exception):
        # Create ledger if not exists 
        if not dbms_cmd.create_table(conn=conn, db_name='blockchain', table_name='ledger', exception=exception):
            print('Failed to create table blockchain.ledger') 

    # Pull blockchain & declare node if not exists 
    if blockchain_cmd.pull_json(conn=conn, master_node='local', exception=exception):
        blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=config['node_type'],
                                                   where=['ip=%s' % config['external_ip'],
                                                          'port=%s' % config['anylog_tcp_port']],
                                                   exception=exception)
        if blockchain == {} or blockchain == []:
            if 'master_node' in config: 
                new_policy = declare_node.declare_node(config=config, location=location) 
                post_policy = blockchain_cmd.post_policy(conn=conn, policy=new_policy, master_node=config['master_node'], exception=exception)
            else: 
                print('Unable to declare policy, missing master_node in config')

            if post_policy is True and blockchain_cmd.pull_json(conn=conn, master_node='local', exception=exception):
                blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type=config['node_type'],
                                                           where=['ip=%s' % config['external_ip'],
                                                                  'port=%s' % config['anylog_tcp_port']],
                                                           exception=exception)
                if len(blockchain) == 0: 
                    print('Failed to declare policy')

    # blockchain sync 
    if not blockchain_cmd.blockchain_sync(conn=conn, source='dbms', time='1 minute', connection=None, exception=exception):
        print('Failed to set blockchain sync process') 

    # Post scheduler 1
    if not rest.post_cmd.start_scheduler1(conn=conn, exception=exception):
        print('Failed to start scheduler 1')

