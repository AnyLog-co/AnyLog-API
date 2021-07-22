import json 
import requests 

def get(conn:str, cmd:str, timeout:float=10, auth:tuple=None, exception:bool=True, remote_query:bool=False):
    """
    Generic REST GET command
    :args: 
       conn:str - REST connection information 
       cmd:str - command to execute 
       timeout:float - length of time to attempt GET request 
       auth:tuple - authentication information (user, password) 
       exception:bool whether or not to print exception messages 
       remote_query:bool - execute query remotely 
    :param: 
       output - results from request 
       headers:dict - REST header info
    :return: 
       if success get content else, 
    """
    output = None 
    headers = {
        'command': cmd, 
        'User-Agent': 'AnyLog/1.23'
    }
    if remote_query == True: 
        headers['destination'] = 'network'
    try: 
        r = requests.get('http://%s' % conn, headers=headers, timeout=timeout, auth=auth)
    except Exception as e: 
        if exception == True: 
            print("Failed to execute cmd '%s' (Error: %s)" % (cmd, e))
    else:
        try: 
            output = r.json() 
        except json.decoder.JSONDecodeError: 
            output = r.text
        except Exception as e: 
            if exception == True: 
                print('Failed to convert query result content into either JSON or raw text (Error: %s)' % e)
    return output 
   
def get_location()->str: 
    """
    Get location using https://ipinfo.io/json 
    :param: 
        location:str - location information from request (default: 0.0, 0.0) 
    :return: 
        location
    """
    location = "0.0, 0.0" 
    try: 
        r = requests.get("https://ipinfo.io/json")
    except Exception as e: 
        pass 
    else: 
        if r.status_code == 200: 
            try: 
                location = r.json()['loc']
            except Exception as e: 
                pass 
    return location 

def post(conn:str, cmd:str, timeout:float=10, auth:tuple=None, exception:bool=True)->bool:
    """
    Generic POST command
    :args: 
       conn:str - REST connection information 
       cmd:str - command to execute 
       timeout:float - length of time to attempt GET request 
       auth:tuple - authentication information (user, password) 
       exception:bool whether or not to print exception messages 
    :param: 
       status:bool 
       headers:dict - REST header info
    :return: 
        status
    """ 
    status = True 
    headers = { 
        'command': cmd, 
        'User-Agent': 'Anylog/1.23'
    }

    try: 
        r = requests.post('http://%s' % conn, headers=headers, timeout=timeout, auth=auth)
    except Exception as e: 
        if exception == True: 
            print('Failed to POST data into AnyLog conn %s (Error: %s)' % (conn, e))
        status = False 
    else: 
        if r.status_code != 200: 
            if exception == True: 
                print('Failed to send data into AnyLog %s due to network code %s' % (conn, r.status_code))
            status = False 

    return status 


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

