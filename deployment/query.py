import import_packages
import_packages.import_dirs()
import post_cmd
import anylog_api
import blockchain_cmd
import dbms_cmd
import policy_cmd
import create_declaration


def query_init(conn:anylog_api.AnyLogConnect, config:dict, disable_location:bool=True, declare_blockchain:bool=True,
               exception:bool=False):
    """
    Deploy a query node instance via REST 
    :definition: 
        Nodes dedicated to query and BI activity
    :args:
       anylog_conn:anylog_api.AnyLogConnect - Connection to AnyLog 
       config:dict - config data (from file + hostname + AnyLog) 
       disable_location:bool - whether or not to have disable_location in policy
       declare_blockchain:bool - whether or not to add Query policy to blockchain
       exception:bool - whether or not to print exception to screen 
    :params: 
        status:bool 
        new_system:bool - variable to check whether we are dealing with a new setup or not
        blockchain:dict - content from blockchain
        new_policy:dict - declaration of policy
    """
    # Create system_query & blockchain
    dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)

    if 'system_query' not in dbms_list:
        if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name='system_query', exception=exception):
            print('Failed to start system_query database')

    if declare_blockchain is True:
        node_id = policy_cmd.declare_anylog_policy(conn=conn, policy_type=config['node_type'], config=config,
                                                   master_node=config['master_node'], disable_location=disable_location,
                                                   exception=exception)
        if node_id is None:
            print('Failed to add % node to blockchain' % config['node_type'])




