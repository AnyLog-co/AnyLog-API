import json 
import requests 

def post_policy(conn:str, policy:dict, timeout:float=10, auth:tuple=None, exception:bool=True, master_node:str="!master_node")->bool:
    """
    POST policy to blockchain
    :args: 
       conn:str - REST connection information 
       policy:dict - policy to POST to blockchain
       timeout:float - length of time to attempt GET request 
       auth:tuple - authentication information (user, password) 
       exception:bool whether or not to print exception messages 
       master_node:str - master_node information 
    :param: 
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
    if isinstance(policy, dict): 
        raw_data = "<policy=%s>" % json.dumps(policy) 
    else: 
        raw_data="<policy=%s>" % policy

    try:
        r = requests.post('http://%s' % conn, headers=headers, timeout=timeout, auth=auth, data=raw_data) 
    except Exception as e: 
        if exception == True: 
            print('Failed to POST data to %s (Error: %s)' % (conn, e))
        status = False 
    else: 
        if r.status_code != 200: 
            if exception == True: 
                print('Failed to send data into AnyLog %s due to network code %s' % (conn, r.status_code)) 
            status = False 
    return status 

