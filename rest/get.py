import requests 

def rest_query(conn:str, command:str, auth:tuple=None, query:bool=False, timeout:int=30): 
    """
    requests GET command
    :args: 
        conn:str - REST connection info 
        command:str - Command to execute 
        auth:tuple - Authentication information
        query:bool - whether to query locally or against network
        timeout:int - REST timeout
    :param: 
        error:str - If exception during error 
        headers:dict - REST header 
    :return: 
        result from REST request
    """
    error = None 
    headers = {
        'command': command, 
        'User-Agent': 'AnyLog/1.23'
    } 
    if query == True: 
        headers['destination'] = 'network' 
    
    try: 
        r = requests.get('http://%s' % conn, auth=auth, headers=headers, timeout=timeout)
    except Exception as e: 
        error = e  
        r = False 

    return r, error 

