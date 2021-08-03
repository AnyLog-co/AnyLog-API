"""
The following scripts assist with the basic deployment of a node publisher and operator node
--> `run publisher` 
--> `run operator` 
--> `set buffer` 
"""
import rest 

def publisher(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True, compress_json:bool=True, move_json:bool=True, master_node:str="!master_node", db_name:str="file_name[0]", table_name:str="file_name[1]")->bool: 
    """
    Execute `start publisher` 
    :command: 
        run publisher where compress_json = true and move_json = true and master_node = !master_node and dbms_name = file_name[0] and table_name = file_name[1]
    :args: 
        conn:str - REST connection information 
        timeout:float - REST timeout 
        auth:tuple - authentication information
        exception:bool - whether to print error messages or not
        compress_json:bool - for publisher process whether to compress the json 
        move_json:bool - for publisher process move to bkup_dir 
        master_node:str - master node information 
        db_name:str - logical database name to store data in
        table_name:str - table within db_name to store data in 
    :param: 
        status:bool 
        cmd:str - command to execute
    :return: 
        status 
    """
    cmd = "run publisher where compress_json=%s and move_json=%s and master_node=%s and dbms_name=%s and table_name=%s" % (compress_json, move_json, master_node, db_name, table_name)
    status = rest.post(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    if status == False and exception == True: 
        print("Failed to start `run publisher` process") 
    return status 

def operator(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True, create_table:bool=True, update_tsd_info:bool=True, archive:bool=True, distributor:str=True, master_node:str="!master_node")->bool: 
    """
    Execute `start operator` 
    :command: 
        run operator where create_table = true and update_tsd_info = true and archive = true and distributor = true and master_node = !master_node
    :args: 
        conn:str - REST connection information 
        timeout:float - REST timeout 
        auth:tuple - authentication information
        exception:bool - whether to print error messages or not
        create_table:bool - whether to create table when new file arrives if table DNE 
        update_tsd_info:bool - Update the tsd table based on 
        archive:bool - A file with stored data will be sent to archive (for distribution) rather than bkup dir
        distribution:bol - If part of a cluster share data once in archive
        master_node:str - master node information 
    :param: 
        status:bool 
        cmd:str - command to execute
    :return: 
        status 
    """
    cmd="run operator where create_table=%s and update_tsd_info=%s and archive=%s and distributor=%s and master_node=%s" % (create_table, update_tsd_info, archive, distributor, master_node)
    status = rest.post(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    if status == False and exception == True: 
        print("Failed to start `run operator` process") 
    return status 

def buffer_threshold(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True)->bool:
    """
    Update buffer to be immediate rather than a 1 minute buffer. 
    :command: 
        set buffer threshold where write_immediate = true
    :args: 
        conn:str - REST connection information 
        timeout:float - REST timeout 
        auth:tuple - authentication information
        exception:bool - whether to print error messages or not
    :param: 
        status:bool 
        comd:str - command to execute
    :return: 
        status
    """
    cmd = "set buffer threshold where write_immediate = true" 
    status = rest.post(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    if status == False and exception == True: 
        print("Failed to start `run operator` process") 
    return status 
