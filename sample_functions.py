"""
The following are some sample functions for AnyLog Network that would assist in processes other than start-up
https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#get-command
"""
import rest 

def get_event_log(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True):
    """
    Execute `get event log` - the last commands processed by the node. adding a list of keywords narrows the output to log events containing the keywords.
    :args: 
       conn:str - rest connection information 
       timeout:float - length of time to attempt get request 
       auth:tuple - authentication information (user, password) 
       exception:bool whether or not to print exception messages 
    :param: 
       cmd:str command to execute 
       output - results from request 
    """
    cmd = "get event log" 
    output = rest.get(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    print(output) 

def get_error_log(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True):
    """
    Execute `get error log` - The last commands that returned an error. Adding a list of keywords narrows the output to error events containing the keywords.
    :args: 
       conn:str - rest connection information 
       timeout:float - length of time to attempt get request 
       auth:tuple - authentication information (user, password) 
       exception:bool whether or not to print exception messages 
    :param: 
       cmd:str command to execute 
       output - results from request 
    """
    cmd = "get error log" 
    output = rest.get(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    print(output) 


def get_node_status(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True):
    """
    Get summary of node` status
    --> `get disk usage`  - Disk statistics about the provided path. 
    --> `get memory info` - Info on the type and version of the OS, node name and type of processor.
    --> `get cpu info` - Info on the CPU of the current node. The function depends on psutil installed.
    --> `get cpu temperature` - The CPU temperature.
    :args: 
       conn:str - REST connection information 
       cmd:str - command to execute 
       timeout:float - length of time to attempt GET request 
       auth:tuple - authentication information (user, password) 
       exception:bool whether or not to print exception messages 
    :param: 
       cmds:dict - command(s) to execute 
       output - results from request 
    """
    cmds = {'disk usage': 'get disk usage /', 'memory info': 'get memory info', 'cpu info': 'get cpu info', 'cpu temp': 'get cpu temperature'}

    for key in list(cmds.keys()): 
        print(key) 
        output = rest.get(conn=conn, cmd=cmds[key], timeout=timeout, auth=auth, exception=exception)
        print(output) 

def get_streaming(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True):
    """
    Execute `get streaming` - Information on REST API calls from external applications
    :args: 
       conn:str - REST connection information 
       cmd:str - command to execute 
       timeout:float - length of time to attempt GET request 
       auth:tuple - authentication information (user, password) 
       exception:bool whether or not to print exception messages 
    :param: 
       cmd:str command to execute 
       output - results from request 
    """
    cmd = "get streaming" 
    output = rest.get(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    print(output) 

def get_rest(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True):
    """
    Execute `get rest` - Information on REST API calls 
    :args: 
       conn:str - REST connection information 
       cmd:str - command to execute 
       timeout:float - length of time to attempt GET request 
       auth:tuple - authentication information (user, password) 
       exception:bool whether or not to print exception messages 
    :param: 
       cmd:str command to execute 
       output - results from request 
    """
    cmd = "get rest" 
    output = rest.get(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    print(output) 


def get_processes(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True):
    """
    Execute `get processes`  - List of processes running on a given node
    :args: 
       conn:str - REST connection information 
       cmd:str - command to execute 
       timeout:float - length of time to attempt GET request 
       auth:tuple - authentication information (user, password) 
       exception:bool whether or not to print exception messages 
    :param: 
       cmd:str command to execute 
       output - results from request 
    """
    cmd = "get streaming" 
    output = rest.get(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    print(output) 

def get_operator(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True):
    """
    Execute `get operator` - Information on the Operator processes. 
    :args: 
       conn:str - REST connection information 
       cmd:str - command to execute 
       timeout:float - length of time to attempt GET request 
       auth:tuple - authentication information (user, password) 
       exception:bool whether or not to print exception messages 
    :param: 
       cmd:str - command to execute 
       output - results from request 
    """
    cmd = "get operator" 
    output = rest.get(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    print(output) 


def get_queries_time(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True):
    """
    Execute `get queries time` - Statistics on queries execution time. The statistics is configurable by the command set query log profile [n] seconds
    :args: 
       conn:str - REST connection information 
       cmd:str - command to execute 
       timeout:float - length of time to attempt GET request 
       auth:tuple - authentication information (user, password) 
       exception:bool whether or not to print exception messages 
    :param: 
       cmd:str - command to execute 
       output - results from request 
    """
    cmd = "get queries time" 
    output = rest.get(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    for key in output['Queries Statistics']: 
        print(key, ": ", output['Queries Statistics'][key]) 

def get_tables(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True, db_name='*'):
    """
    execute `get tables where dbms=?` - the list of tables of the named database and where the table is declared (local database and/or blockchain)
    :args: 
       conn:str - rest connection information 
       cmd:str - command to execute 
       timeout:float - length of time to attempt get request 
       auth:tuple - authentication information (user, password) 
       exception:bool whether or not to print exception messages 
       db_name:str - logical database name to check tables for. if '*' gets list of all tables 
    :param: 
       cmd:str - command to execute 
       output - results from request 
    """
    cmd = "get tables where dbms=%s" % db_name

    output = rest.get(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    print(output) 

def get_row_count(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True):
    """
    Execute `get rows count` - Details the number of rows in all or specified tables. Details are available here.
    :args: 
       conn:str - rest connection information 
       cmd:str - command to execute 
       timeout:float - length of time to attempt get request 
       auth:tuple - authentication information (user, password) 
       exception:bool whether or not to print exception messages 
    :param: 
       cmd:str - command to execute 
       output - results from request 
    """
    cmd = "get rows count"
    output = rest.get(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    print(output) 

def execute_query(conn:str, db_name:str, cmd:str, timeout:float=10, auth:tuple=None, exception:bool=True):
    """
    Execute `run client () sql db_name "select ...."` - Details the number of rows in all or specified tables. Details are available here.
    :args: 
       conn:str - rest connection information 
       cmd:str - command to execute 
       db_name:str - logical database 
       timeout:float - length of time to attempt get request 
       auth:tuple - authentication information (user, password) 
       exception:bool whether or not to print exception messages 
       db_name:str - logical database name to check tables for. if '*' gets list of all tables 
    :param: 
       output - results from request 
    """
    cmd = 'sql %s "%s"' % (db_name, cmd) 
    output = rest.get(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception, remote_query=True)
    print(output) 

if __name__ == '__main__': 
    conn = '20.97.12.66:2049' 
    timeout=10
    auth=None
    exception=False 
    db_name="aiops" 

    #get_event_log(conn=conn, timeout=timeout, auth=auth, exception=exception, remote_query=True)
    #get_error_log(conn=conn, timeout=timeout, auth=auth, exception=exception, remote_node=None)
    #get_node_status(conn=conn, timeout=timeout, auth=auth, exception=exception, remote_node=None)
    #get_streaming(conn=conn, timeout=timeout, auth=auth, exception=exception, remote_node=None)
    #get_rest(conn=conn, timeout=timeout, auth=auth, exception=exception, remote_node=None) 
    #get_processes(conn=conn, timeout=timeout, auth=auth, exception=exception, remote_node=None) 
    #get_queries_time(conn=conn, timeout=timeout, auth=auth, exception=exception, remote_node=None)
    #get_tables(conn=conn, timeout=timeout, auth=auth, exception=exception, remote_node=None, db_name='*')
    #execute_query(conn=conn, db_name="aiops", cmd="select count(*) from fic11_fb_fsetpointvalue;", timeout=timeout, auth=auth, exception=exception)
    
    # Requires conn to Operator node 
    #get_row_count(conn=conn, timeout=timeout, auth=auth, exception=exception, remote_node=None) 
    #get_operator(conn=conn, timeout=timeout, auth=auth, exception=exception, remote_query=True)
