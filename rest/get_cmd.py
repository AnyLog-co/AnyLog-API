import rest 

def __get_error(conn:str, r, error, exception:bool=True)->bool: 
    """
    Print error if case
    :args: 
        conn:str - REST connection info 
        r, error - results from GET request
        exection:bool - whether to screen print exception or not
    :params: 
        status:bool 
    :return:
        status 
    """
    status = False
    if r == False and isinstance(error, str): 
        if exception == True: 
            print('Failed to excute GET on %s (Error: %s)' % (conn, error)) 
        status = True
    elif r == False and isinstance(error, int):
        if exception == True: 
            print('Failed to execute GET on %s due to network error %s' % (conn, error))
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
    if __get_error(conn.conn, r, error, exception=True) == False: 
        try: 
            print(r.text)
        except Exception as e: 
            print('Failed to extract help information (Error: %s) ' % e)

def get_status(conn:rest.AnyLogConnect, exception:bool=False)->bool: 
    """
    Execute get status
    :args: 
        conn:rest.AnyLogConnect - Connection to AnyLog 
        exception:bool - whether to print execptions or not 
    :params: 
        status:bool
    :return: 
        stattus
    """
    status = True
    r, error = conn.get(command='get status', query=False)
    
    if __get_error(conn.conn, r, error, exception) == False: 
       if 'running' not in r.text or 'not' in r.text: 
           status = False
    else: 
        status = False 

    return status

def get_dictionary(conn:rest.AnyLogConnect, exception:bool=False)->dict: 
    """
    Extract raw dictionary from AnyLog
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :params: 
        data:str - raw dictionary data
    :return: 
        data
    """
    
    r, error = conn.get(command='get dictionary', query=False)

    if __get_error(conn.conn, r, error, exception=True) == False: 
        try: 
            data = r.text 
        except Exception as e: 
            if exception == True: 
                print('Failed to get dictionary from: %s (Error: %s)' % (conn, e))
            data = None 

    return data


def get_hostname(conn:rest.AnyLogConnect, exception:bool=False)->str: 
    """
    Extract hostname
    :args: 
        conn:rest.AnyLogConnect - connection to AnyLog RESt 
        exception:bool - whether to print errors to screen 
    :params: 
        hostname:str - hostname
    :return: 
        hostname
    """
    hostname = None 
    r, error = conn.get(command='get hostname', query=False)
    if __get_error(conn.conn, r, error, exception=True) == False: 
        try: 
            hostname = r.text
        except Exception as e: 
            print('Failed to extract hostname from %s (Error: %s)' % (conn, e))

    return hostname

