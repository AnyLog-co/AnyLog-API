import rest 

def blockchain_sync(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True, source:str="master", sync_time:str="15 seconds", connection:str="!master_node")->bool:
    """
    Init blockchain sync process 
    :args: 
        conn:str - REST connection information
        timeout:float - wait time before timeout 
        auth:tuple - authentication information 
        exception:bool - whether to print exceptions or not 
        source:str - source to get data from 
        sync_time:str - frequency of how often to sync blockchain 
        connection:str - blockchain connection informaiton
    :param: 
        status:bool 
        cmd:str - command to execute 
    :return: 
        status 
    """
    cmd = "run blockchain sync where source=%s and time=%s and dest=file" % (source, sync_time)
    if connection != None: 
        cmd += " and connection=%s" % connection
    status = rest.post(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    return status 

def schedule_one(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True)->bool: 
    """
    Init schedule 1 
    :args: 
        conn:str - REST connection information
        timeout:float - wait time before timeout 
        auth:tuple - authentication information 
        exception:bool - whether to print exceptions or not 
    :param: 
        status:bool 
        cmd:str - command to execute 
    :return: 
        status 
    """
    cmd = "run scheduler 1"
    status = rest.post(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    return status 


