import rest 

def __get_error(r, error)->bool: 
    """
    Print error if case
    :args: 
        r, error - results from GET request
    :params: 
        status:bool 
    :return:
        status 
    """
    status = False
    if r == False and isinstance(error, str): 
        print('Failed to excute GET on %s (Error: %s)' % (conn.conn, error)) 
        status = True
    elif r == False and isinstance(error, int):
        print('Failed to execute GET on %s due to network error %s' % (conn.conn, error))
        status = True

    return status 
 
def get_help(conn:rest.AnyLogConnect, command:str=None): 
    """
    Execute 'help' against AnyLog. If command is set get help regarding command
    :args: 
        conn:rest.AnyLogConnect - Connection to AnyLog 
        command:str - command to get help on 
    :note: 
        function prints results rather than return it
    """
    status = True
    help_stmt = 'help'     
    if command != None: 
        help_stmt += " " + command

    r, error = conn.get(command=help_stmt)
    if __get_error(r, error) == False: 
        try: 
            print(r.text)
        except Exception as e: 
            print('Failed to extract help information (Error: %s) ' % e)

def get_status(conn:rest.AnyLogConnect)->bool: 
    """
    Execute get status
    :args: 
        conn:rest.AnyLogConnect - Connection to AnyLog 
    :params: 
        status:bool
    :return: 
        stattus
    """
    status = True
    r, error = conn.get(command='get status', query=False)
    
    if __get_error(r, error) == False: 
       if 'running' not in r.text or 'not' in r.text: 
           status = False
    else: 
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

