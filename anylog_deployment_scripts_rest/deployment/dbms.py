import rest

def connect(conn:str, db_conn:str, db_port:int, db_type:str="sqlite", db_name:str="system_query", timeout:float=10, auth:tuple=None, exception:bool=True)->bool: 
    """
    Connect to database 
    :args: 
        db_conn:str - database connection info (user@ip:passwd) 
        db_port:int - database port 
        db_type:int - database type (PSQL or SQLite)
        db_name:str - logical database name
        conn:str - REST connection information
        timeout:float - REST timeout 
        auth:tuple - REST authentication 
        exception:bool - print exception messages
    :param: 
        status:bool 
        cmd:str - Command to execute
    :return: 
        status 
    """
    cmd = "connect dbms %s %s %s %s" % (db_type, db_conn, db_port, db_name) 
    status = rest.post(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    return status 

def create_table(table:str, db_name:str, conn:str, timeout:float=10, auth:tuple=None, exception:bool=True)->bool: 
    """
    Create based on AnyLog (table must exist in blockchain)
    :args: 
        table:str - Table name 
        db_name:str - logical database 
        conn:str - REST connection information
        timeout:float - REST timeout 
        auth:tuple - REST authentication 
        exception:bool - print exception messages
    :param: 
        status:bool 
        cmd:str - Command to execute 
    :return: 
        status 
    """
    cmd="create table %s where dbms=%s" % (table, db_name)  
    status = rest.post(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    return status 
