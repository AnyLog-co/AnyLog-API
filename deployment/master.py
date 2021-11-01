import __init__
import anylog_api
import blockchain_cmd
import dbms_cmd
import policy_cmd


def master_init(conn:anylog_api.AnyLogConnect, config:dict, disable_location:bool=True, exception:bool=False):
    """
    Deploy a master node instance via REST 
    :definition: 
        A "notary" system between other nodes in the network via either a public or private blockchain
    :args:
       anylog_conn:anylog_api.AnyLogConnect - Connection to AnyLog 
       disable_location:bool -whether or not to have location in policy
       config:dict - config data (from file + hostname + AnyLog) 
       exception:bool - whether or not to print exception to screen 
    :params: 
        status:bool 
        new_system:bool - variable to check whether we are dealing with a new setup or not
        blockchain:dict - conetent from blockchain
        new_policy:dict - decleration of policy
    """
    # Create system_query & blockchain
    dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
    if 'blockchain' not in dbms_list:
        if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name='blockchain', exception=exception):
            print('Failed to start blockchain database')

    # Create table ledger
    if not dbms_cmd.get_table(conn=conn, db_name='blockchain', table_name='ledger', exception=exception):
        # Create ledger if not exists 
        if not dbms_cmd.create_table(conn=conn, db_name='blockchain', table_name='ledger', exception=exception):
            print('Failed to create table blockchain.ledger')

    blockchain_cmd.blockchain_sync_scheduler(conn=conn, source='dbms', time="30 seconds",
                                             master_node=config['master_node'], exception=exception)

    node_id = policy_cmd.declare_anylog_policy(conn=conn, policy_type=config['node_type'], config=config,
                                             master_node='local', disable_location=disable_location, exception=exception)
    print(node_id) 
    if node_id is None:
        print('Failed to add %s node to blockchain' % config['node_type'])
