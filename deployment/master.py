
import __init__
import declare_node
import rest.anylog_api as anylog_api
import rest.blockchain_cmd as blockchain_cmd
import rest.dbms_cmd as dbms_cmd
import rest.post_cmd as post_cmd
import rest.anylog_api as post_cmd

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
    status = True 
    # Create system_query & blockchain 
    new_system = False
    dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
    if dbms_list == 'No DBMS connections found': 
        new_system = True
    if new_system == True or 'system_query' not in dbms_list: 
        status = dbms_cmd.connect_dbms(conn=conn, config={}, db_name='system_query', exception=exception) 
        if status == False: 
            print('Failed to start system_query database') 
    if new_system == True or 'blockchain' not in dbms_list: 
        status = dbms_cmd.connect_dbms(conn=conn, config=config, db_name='blockchain', exception=exception) 
        if status == False: 
            print('Failed to start blockchain database') 
    # Create table ledger 
    if status == True and dbms_cmd.check_table(conn=conn, db_name='blockchain', table_name='ledger', exception=exception) == False: 
        # Create ledger if not exists 
        status = dbms_cmd.create_table(conn=conn, db_name='blockchain', table_name='ledger', exception=exception)
        if status == False: 
            print('Failed to create table blockchain.ledger') 

    # Pull blockchain & declare node if not exists 
    if blockchain_cmd.pull_json(conn=conn, master_node='local', exception=exception) == True: 
        blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type='master', where=['ip=%s' % config['external_ip']], exception=exception) 
        if blockchain == {} or blockchain == []: 
            if 'master_node' in config: 
                new_policy = declare_node.declare_node(config=config, location=location) 
                status = blockchain_cmd.post_policy(conn=conn, policy=new_policy, master_node=config['master_node'], exception=exception)
            else: 
                print('Unable to declare policy, missing master_node in config')

            if status == True and blockchain_cmd.pull_json(conn=conn, master_node='local', exception=exception) == True: 
                blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type='master', where=['ip=%s' % config['external_ip']], exception=exception) 
                if len(blockchain) == 0: 
                    print('Failed to declare policy')

    # blockchain sync 
    status = blockchain_cmd.blockchain_sync(conn=conn, source='dbms', time='1 minute', connection=None, exception=exception)
    if status == False: 
        print('Failed to set blockchain sync process') 

    # Post scheduler 1 
    if not post_cmd.post_scheduler1(conn=conn, exception=exception):
        print('Failed to start scheduler 1') 

