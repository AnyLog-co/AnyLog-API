"""
The following are simple methods used throughout the code, but aren't necesserily part of the code
Examples:
    * Error messages
    * String formatting
"""


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
    base_error = 'Failed to execute %s against %s for: %s' % (request_type.upper(), conn, command)
    if r is False:
        status = True
        if isinstance(error, str) and exception is True:
            print(base_error + " (Error: %s)" % error)
        elif isinstance(error, int) and exception is True:
            print(base_error + " (Network Error: %s)" % error)
        elif exception is False:
            print(base_error)
    return status


def format_string(key:str, value:str)->str:
    """
    For blockchain WHERE conditions format key value pairs
        if value is string: key="value"
        else: key=value
    :args:
        key:str - key
        value:str - value
    :params:
        frmt_string:str - formatted string
    :return:
        frmt_string
    """
    if isinstance(value, str):
        value = value.replace('"', '').replace("'", "").lstrip().rstrip()

    frmt_string = '%s="%s"' % (key, value)
    """
    if isinstance(value, str) and (" " in value or "+" in value):
        frmt_string = '%s="%s"' % (key, value)
    else:
        frmt_string = "%s=%s" % (key, value)
    """
    return frmt_string
