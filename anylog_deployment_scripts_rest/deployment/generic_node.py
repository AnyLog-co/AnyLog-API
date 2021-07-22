import blockchain
import dbms 
import rest
import scheduler
import start_methods
 

def init(conn:str, anylog_params:dict, timeout:float=10, auth:tuple=None, exception:bool=True, init_blockchain:bool=False, master_node:str="!master_node", remove_buffer:bool=False):
    """
    Process to deploy a query or publisher node
    :args: 
        conn:str - REST connection information
        anylog_params:dict - AnyLog dictionary params
        timeout:float - REST timeout time 
        auth:tuple - REST authentication information
        exception:bool - whether or not to print exception messages
        blockchain:bool - Whether or not to add policy to blockchain
        master_node:str - master node information
        remove_buffer:bool - Remove buffer time for inserts
    :param: 
        status:bool 
    :return: 
        status 
    """
    status = True 
    # connect DBMS
    if 'node_type' in anylog_params and anylog_params['node_type'] != 'query': 
        status = dbms.connect(db_conn=anylog_params['db_user'], db_port=anylog_params['db_port'], db_type=anylog_params['db_type'], db_name="system_query", conn=conn, timeout=timeout, auth=auth, exception=exception)
    elif 'db_type' in anylog_params and 'db_user' in anylog_params and 'db_port' in anylog_params: 
        status = dbms.connect(db_conn=anylog_params['db_user'], db_port=anylog_params['db_port'], db_type=anylog_params['db_type'], db_name="system_query", conn=conn, timeout=timeout, auth=auth, exception=exception)
    else: 
        if exception == True: 
            print("Missing one or more config params: 'db_type', 'db_user' and 'db_port") 
        status = False 
    if status == False: 
        print('Failed to connect to system_query database. Cannot continue') 
        return status 
    status = blockchain.pull_json(conn=conn, timeout=timeout, auth=auth, exception=exception, master_node=master_node)
    if status == False: 
        if exception == True: 
            print('Falied to pull blockchain for validation')
        return status 

    where_condition = ""
    if 'company_name' in anylog_params: 
        where_condition += "company='%s'" % anylog_params['company_name']
    if 'ip' in anylog_params: 
        if where_condition != "": 
            where_condition += " and ip=%s" % anylog_params['ip'] 
        else: 
            where_condition = "ip=%s" % anylog_params['ip'] 
    if "anylog_server_port" in anylog_params: 
        if where_condition != "": 
            where_condition += " and port=%s" % anylog_params['anylog_server_port'] 
        else: 
            where_condition += "port=%s" % anylog_params['anylog_server_port'] 

    output = blockchain.get_policy(conn=conn, timeout=timeout, auth=auth, exception=exception, policy="*", where=where_condition) # check if exists a policy with the where condition 
    if output == {}: 
        init_blockchain = True
    
    if init_blockchain == True:  
        status = blockchain.declare_policy(conn=conn, anylog_params=anylog_params, timeout=timeout, auth=auth, exception=exception)
        if status == False and exception == True: 
            print('Failed to declare policy in blockchain') 
        elif output != {} and status == True: 
            print('Note - there now exists 2 types of policies with the same information') 
    
    # pull blockchain
    status = blockchain.pull_json(conn=conn, timeout=timeout, auth=auth, exception=exception, master_node=master_node)

    status = scheduler.blockchain_sync(conn=conn, timeout=timeout, auth=auth, exception=exception, source="master", sync_time="15 seconds", connection=master_node) 
    if status == False and exception == True: 
        print('Failed to configure blockchain sync process') 

    # Start publisher process 
    if 'node_type' in anylog_params and anylog_params['node_type'] == 'publisher': 
        status = start_methods.publisher(conn=conn, timeout=timeout, auth=auth, exception=exception, compress_json=True, move_json=True, master_node=master_node, db_name="file_name[0]", table_name="file_name[0]") 
        if status == True and remove_buffer == True: 
            status=start_methods.buffer_threshold(conn=conn, timeout=timeout, auth=auth, exception=exception)
    return status  


