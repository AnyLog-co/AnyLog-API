import ast
import rest 

def blockchain_get(conn:str, policy_type:str='*', where:list=[], bring:str=None, separator:str=None, auth:tuple=None, timeout:int=30)->list: 
    """
    blockchain GET command 
    :args: 
        conn:str - REST connection info
        policy_type:str - policy type to get (default: all) 
        where:list - where condition (ex. [ip='127.0.0.1', port=2048])
        bring:list - values to extract from blockchain
        separator:str - how to separate results 
        auth:tuple - Authentication information
        timeout:int - REST timeout
    :param: 
        cmd:str - command to execute 
        blockchain:list - data extracted  
    """
    cmd = "blockchain get %s" % policy_type
    if where != []: 
        cmd += " where" 
        for value in where:
           cmd += " " + value
    if bring != None: 
        cmd += " bring %s" % bring 
    if separator != None: 
        cmd += " separator=%s" % separator

    blockchain = []
    r, error = rest.get(conn=conn, command=cmd, auth=auth, timeout=timeout)
    if r != False and r.status_code == 200: 
        try: 
            blockchain = r.json()['Blockchain data'].split(separator)
        except: 
            try: 
                blockchain = ast.literal_eval(r.text)
            except: 
                blockchain = r.text
    return blockchain 

def check_table(conn:str, db_name:str, table_name:str, auth:tuple=None, timeout:int=30)->bool: 
    """
    Check if table exists blockchain 
    :args: 
        conn:str - REST connection info
        db_name:str - database you'd like to use
        table_name:str - table you'd like to ccheck
        auth:tuple - Authentication information
        timeout:int - REST timeout
    :param: 
        cmd:str - command to execute 
        status:bool
    """
    status = False 
    cmd = "get table blockchain status where dbms = %s and name = %s" % (db_name, table_name)
    
    r, e = rest.get(conn=conn, command=cmd, auth=auth, timeout=timeout) 
    try: 
        if r.json()['local'] == 'true':
            status = True 
    except: 
        if 'true' in r.text: 
            status = True

    return status 


def pull_json(conn:str, master_node:str='local', db_name:str, table_name:str, auth:tuple=None, timeout:int=30)->bool: 
    """
    Check if table exists blockchain 
    :args: 
        conn:str - REST connection info
        master_node:str - master node
        db_name:str - database you'd like to use
        table_name:str - table you'd like to ccheck
        auth:tuple - Authentication information
        timeout:int - REST timeout
    :param: 
        cmd:str - command to execute 
        status:bool
    """
    cmd = "blockchain pull to json !blockchain_file"

