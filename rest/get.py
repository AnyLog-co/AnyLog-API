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


