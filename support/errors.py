def get_error(conn:str, r, error, exception:bool=True)->bool: 
    """
    Print error for GET command 
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
 
def post_error(conn:str, r, error, exceptio:bool=True)->bool: 
    """
    Print error for POST command 
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
            print('Failed to excute POST on %s (Error: %s)' % (conn.conn, error)) 
        status = True 
    elif r == False and isinstance(error, int):
        if exception == True: 
            print('Failed to execute POST on %s due to network error %s' % (conn.conn, error))
        status = True

    return status 
