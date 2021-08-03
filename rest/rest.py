import requests 
"""
The folloowing are the base support for AnyLog via REST 
- GET: extract information from AnyLog (information + queries)
- POST: Execute or POST command against AnyLog 
- POST_POLICY: POST information to blockchain
""" 

def get(conn:str, command:str, auth:tuple=None, query:bool=False, timeout:int=30): 
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

def post(conn:str, command:str, auth:tuple=None, timeout:int=30)->bool: 
    """
    Generic POST command
    :args: 
        conn:str - REST connection info
        command:str - command to execute 
        auth:tuple - Authentication information
        timeout:int - REST timeout
    :param: 
        status:bool
        headers:dict - REST header info
    :return: 
        status
    """
    status = True
    headers = {
        'command': command,
        'User-Agent': 'AnyLog/1.23'
    }

    try: 
        r = requests.post('http://%s' % conn, headers=headers, auth=auth, tiemout=timeout)
    except: 
        status = False 
    else: 
        if r.status_code != 200: 
            status = False
    return status 


def post_policy(conn:str, policy:str, master_node:str, auth:tuple=None, timeout:int=30)->bool: 
    """
    POST to blockchain 
    :args: 
        conn:str - REST connection info 
        policy:str - policy to POST to blockchain
        master_node:str - master node to post to 
        auth:tuple - Authentication information 
        timeout:int - REST timeout
    :params: 
       status:bool 
       headers:dict - REST header info
       raw_data:str - data to POST 
    :return: 
        status
    """ 
    status = True 
    headers = { 
        "command": "blockchain push !policy", 
        "destination": master_node,
        "Content-Type": "text/plain",
        "User-Agent": "AnyLog/1.23" 
    }

    raw_data="<policy=%s>" % policy 
    try:
        r = requests.post('http://%s' % conn, headers=headers, timeout=timeout, auth=auth, data=raw_data) 
    except Exception as e: 
        status = False 
    else: 
        if r.status_code != 200: 
            status = False 

    return status 
:
