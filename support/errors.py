def get_error(conn:str, command:str, r, error, exception:bool=True)->bool: 
    """
    Print error for GET command 
    :args: 
        conn:str - REST connection info 
        command:str - command executed 
        r, error - results from GET request
        exection:bool - whether to screen print exception or not
    :params: 
        status:bool 
    :return:
        status 
    """
    status = False
    if r is False: 
        if exception is True:
            print('Failed to execute command: %s' % command)
        if isinstance(error, str): 
            if exception is True: 
                print('Failed to excute GET on %s (Error: %s)' % (conn, error)) 
        elif isinstance(error, int):
            if exception is True: 
                print('Failed to execute GET on %s due to network error %s' % (conn, error))
        status = True

    return status 
 
def post_error(conn:str, command:str, r, error, exception:bool=True)->bool: 
    """
    Print error for POST command 
    :args: 
        conn:str - REST connection info 
        command:str - command executed 
        r, error - results from GET request
        exection:bool - whether to screen print exception or not
    :params: 
        status:bool 
    :return:
        status 
    """ 
    status = False
    if r is False: 
        if exception is True:
            print('Failed to execute command: %s' % command)
        if isinstance(error, str): 
            if exception is True: 
                print('Failed to excute POST on %s (Error: %s)' % (conn, error)) 
        elif isinstance(error, int):
            if exception is True: 
                print('Failed to execute POST on %s due to network error %s' % (conn, error))
        status = True

    return status 

