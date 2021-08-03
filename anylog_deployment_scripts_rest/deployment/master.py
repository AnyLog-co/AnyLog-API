import blockchain
import dbms 
import rest
import scheduler
 

def init(conn:str, anylog_params:dict, timeout:float=10, auth:tuple=None, exception:bool=True, init_blockchain:bool=False):
    """
    Process to deploy a master node
    :args: 
        conn:str - REST connection information
        anylog_params:dict - AnyLog dictionary params
        timeout:float - REST timeout time 
        auth:tuple - REST authentication information
        exception:bool - whether or not to print exception messages
        blockchain:bool - Whether or not to add policy to blockchain
    :param: 
        status:bool 
    :return: 
        status 
    """
    status = True 
    # connect DBMS
    status = dbms.connect(db_conn='user@127.0.0.1:passwd', db_port=0000, db_type="sqlite", db_name="system_query", conn=conn, timeout=timeout, auth=auth, exception=exception)
    if 'db_type' in anylog_params and 'db_user' in anylog_params and 'db_port' in anylog_params: 
        status = dbms.connect(db_conn=anylog_params['db_user'], db_port=anylog_params['db_port'], db_type=anylog_params['db_type'], db_name="blockchain", conn=conn, timeout=timeout, auth=auth, exception=exception)
    else: 
        if exception == True: 
            print("Missing one or more config params: 'db_type', 'db_user' and 'db_port") 
        status = False 
    if status == False: 
        print('Failed to connect to blockchain database. Cannot continue') 
        return status 
    
    # declare policy 
    if init_blockchain == True: 
        status = blockchain.declare_policy(conn=conn, anylog_params=anylog_params, timeout=timeout, auth=auth, exception=exception)
        if status == False and exception == True: 
            print('Failed to declare master in blockchain') 

    # pull blockchain
    status = blockchain.pull_json(conn=conn, timeout=timeout, auth=auth, exception=exception, master_node=None)

    status = scheduler.blockchain_sync(conn=conn, timeout=timeout, auth=auth, exception=exception, source="dbms", sync_time="15 seconds", connection=None)
    if status == False and exception == True: 
        print('Failed to configure blockchain sync process') 

    return status  

