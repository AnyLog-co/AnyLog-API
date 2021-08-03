import rest 

def get_help(conn:str, command:str=None, auth:tuple=None, timeout:int=30): 
    """
    Execute 'help' against AnyLog. If command is set get help regarding command
    :args: 
        conn:str - REST connection
        command:str - command to get help on 
        auth:tuple - REST authentication
        timeout:int - REST timeout
    :note: 
        function prints results rather than return it
    """
    status = True
    help_stmt = 'help'     
    if command != None: 
        help_stmt += " " + command
    r, error = rest.get(conn=conn, command=help_stmt, auth=auth, query=False, timeout=timeout)
    
    if r != False or r.status_code == 200: 
        try: 
            print(r.text)
        except Exception as e: 
            print('Failed to extract help information (Error: %s) ' % e)
    else: 
        print('Command against %s faild (Error: %s)' % (conn, e))

def get_status(conn:str, auth:tuple=None, timeout:int=30)->bool: 
    """
    Execute get status
    :args: 
        conn:str - REST connection
        auth:tuple - REST authentication
        timeout:int - REST timeout
    :params: 
        status:bool
    :return: 
        stattus
    """
    status = True
    r, error = rest.get(conn=conn, command='get status', auth=auth, query=False, timeout=timeout)
    
    if r == False or r.status_code != 200: 
        status = False 
    else: 
       if 'running' not in r.text or 'not' in r.text: 
           status = False
    return status

def get_dictionary(conn:str, auth:tuple=None, timeout:int=30)->dict: 
    """
    Extract dictionary values from AnyLog
    :args: 
        conn:str - REST connection
        auth:tuple - REST authentication
        timeout:int - REST timeout
    :params: 
        data:dict - data extracted from AnyLog
    :return: 
        data
    """
    data = {} 
    r, error = rest.get(conn=conn, command='get dictionary', auth=auth, query=False, timeout=timeout)

    if r != False and r.status_code == 200: 
        try: 
            for value in r.text.split('\n'):
                if value != '\r' and value != '':  
                    data[value.split(':')[0].rstrip().lstrip()] = value.split(':')[-1].split('\r')[0].rstrip().lstrip()
        except Exception as e: 
            print('Failed to get dictionary from: %s (Error: %s)' % (conn, e))
           
    return data


def get_hostname(conn:str, auth:tuple=None, timeout:int=30)->str: 
    """
    Extract hostname
    :args: 
        conn:str - REST connection
        auth:tuple - REST authentication
        timeout:int - REST timeout
    :params: 
        hostname:str - hostname
    :return: 
        hostname
    """
    hostname = None 
    r, error = rest.get(conn=conn, command='get hostname', auth=auth, query=False, timeout=timeout)
    if r != False and r.status_code == 200: 
        try: 
            hostname = r.text
        except Exception as e: 
            print('Failed to extract hostname from %s (Error: %s)' % (conn, e))

    return hostname

