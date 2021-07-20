import time 

import blockchain
import dbms 
import rest
import scheduler
import start_methods
 

def partition(conn:str, dbms:str, timeout:float=10, auth:tuple=None, exception:bool=True, table:str="*", ts_column:str="timestamp", partition:str="1 day")->bool: 
    """
    Execute `partition` process 
    :command: 
        partiton anylog * using timestamp by day 
    :args: 
        conn:str - REST connection information 
        dbms:str - logical database to partition against 
        timeout:float - REST timeout 
        auth:tuple - authentication information
        exception:bool - whether to print error messages or not
        table:str - table to partiiton, if '*' partition all tables in database
        ts_column:str - timestamp column to partiton by
        partition:str - timestamp to partition by [second, minute, hour, day, month] 
    :param: 
        status:bool 
        cmd:str - command to execute
    :return: 
        status 
    """
    cmd = "parition %s %s using %s by %s" % (dbms, table, ts_column, partition) 
    status = rest.post(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    if status == False and exception == True: 
        print("Failed to start `partition` process") 
    return status 

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
    status = dbms.connect(db_conn='user@127.0.0.1:passwd', db_port=0000, db_type="sqlite", db_name="system_query", conn=conn, timeout=timeout, auth=auth, exception=exception)
    if exception == True: 
        print("Missing one or more config params: 'db_type', 'db_user' and 'db_port") 
   
    if status == False and exception == True: 
        print('Failed to connect to system_query database. Cannot continue') 

    if 'default_dbms' in anylog_params: 
        status = dbms.connect(db_conn=anylog_params['db_user'], db_port=anylog_params['db_port'], db_type=anylog_params['db_type'], db_name=anylog_params['default_dbms'], conn=conn, timeout=timeout, auth=auth, exception=exception)
    else: 
        if exception == True: 
            print("Missing 'default_dbms' parameter for AnyLog") 
        status = False 
    if status == False: 
        if exception == True: 
            print("Failed to connect to '%s' database. Cannot continue" ^ anylog_params['default_dbms']) 
        return status 

   
    status = blockchain.pull_json(conn=conn, timeout=timeout, auth=auth, exception=exception, master_node=master_node)
    if status == False: 
        if exception == True: 
            print('Falied to pull blockchain for validation')
        return status 

    if init_blockchain == True: 
        # declare cluster if not exists 
        if 'enable_cluster' in anylog_params and bool(anylog_params['enable_cluster']) == True and 'cluster_id' not in anylog_params:
            # setup cluster name
            if 'cluster_name' not in anylog_params and 'company_name' not in anylog_params:
                anylog_params['cluster_name'] = 'test-cluster' 
            elif 'cluster_name' not in anylog_params:
                anylog_params['cluster_name'] = '%s-cluster' % anylog_params['company_name']

            # declare cluster 
            status = blockchain.declare_cluster(conn=conn, anylog_params=anylog_params, timeout=timeout, auth=auth, exception=exception)
            if status == False: 
                if exception == True: 
                    print('Failed to to declare cluster')
            time.sleep(10) 
            status = blockchain.pull_json(conn=conn, timeout=timeout, auth=auth, exception=exception, master_node=master_node)
            if status == False and exception == True: 
                print('Falied to pull blockchain for validation')

            # get cluster id
            where_condition = 'name="%s"' % anylog_params['cluster_name'] 
            if 'company_name' in anylog_params: 
                where_condition += ' and company="%s"' % anylog_params['company_name'] 
            cluster_id = blockchain.get_policy(conn=conn, timeout=timeout, auth=auth, exception=exception, policy="cluster", where=where_condition, bring="[cluster][id]")
            anylog_params['cluster_id'] = cluster_id['Blockchain data'] 

        status = blockchain.declare_policy(conn=conn, anylog_params=anylog_params, timeout=timeout, auth=auth, exception=exception)
        if status == False and exception == True: 
            print('Failed to post operator to blockchain') 
        status = blockchain.pull_json(conn=conn, timeout=timeout, auth=auth, exception=exception, master_node=master_node)
        if status == False and exception == True: 
            print('Falied to pull blockchain for validation')

    # Add partitions 
    if 'default_dbms' in anylog_params: 
        status = partition(conn=conn, dbms=anylog_params['default_dbms'], timeout=timeout, auth=auth, exception=exception, table="*", ts_column="timestamp", partition="1 day")
        if status == False and exception == True:
            print('Failed to declare partition on all tables for dbms: %s' % anylog_params['default_dbms']) 
    """
    # Add MQTT (not done)
    """


    status = scheduler.blockchain_sync(conn=conn, timeout=timeout, auth=auth, exception=exception, source="master", sync_time="15 seconds", connection=master_node) 
    if status == False and exception == True: 
        print('Failed to configure blockchain sync process') 

    if remove_buffer == True: 
        status=start_methods.buffer_threshold(conn=conn, timeout=timeout, auth=auth, exception=exception)
        if status == False and exception == True: 
            print('Failed to set buffer threshold') 
    if 'master_node' in anylog_params: 
        status = start_methods.operator(conn=conn, timeout=timeout, auth=auth, exception=exception, create_table=True, update_tsd_info=True, archive=True, distributor=True, master_node=anylog_params['master_node'])
    else:
        status = start_methods.operator(conn=conn, timeout=timeout, auth=auth, exception=exception, create_table=True, update_tsd_info=True, archive=True, distributor=True, master_node="!master_node")

    if status == False and exception == True: 
        print('Failed to start run operator process') 

    return status 





        

     
   
