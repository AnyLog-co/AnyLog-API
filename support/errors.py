def print_error(conn:str, request_type:str, command:str, r, error, exception:bool=True)->bool:
    """
    Print exception for GET command
    :args:
        conn:str - REST connection info
        request_type:str - request type (get, put, post)
        command:str - command executed
        r, error - results from GET request
        exception:bool - whether to screen print exception or not
    :params:
        status:bool
        base_error:str - base error message (request type, conn, command)
    :return:
        if no error print False, else print True
    """
    status = False
    base_error = 'Failed to execute %s against %s for "%s"' % (request_type.upper(), conn, command)
    if r is False:
        status = True
        if isinstance(error, str) and exception is True:
            print(base_error + " (Error: %s)" % error)
        elif isinstance(error, int) and exception is True:
            print(base_error + " (Network Error: %s)" % error)
        elif exception is False:
            print(base_error)
    return status


