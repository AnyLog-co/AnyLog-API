from anylog_connection import AnyLogConnection
import support


def get_status(anylog_conn:AnyLogConnection, exception:bool=False)->bool:
    """
    check if node is running
    :args:
        anylog_conn:AnyLogConnection - AnyLog REST connection information
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - running
        False - not running
    """
    status = False
    headers = {
        'command': 'get status',
        'User-Agent': 'AnyLog/1.23'
    }
    r, error = anylog_conn.get(headers=headers)

    if r is False or int(r.status_code) != 200:
        if exception is True:
            support.print_rest_error(error_type='GET', cmd=headers['command'], error=error)
    elif 'running' in r.text and 'not' not in r.text:
        status = True

    return status


def get_dictionary(anylog_conn:AnyLogConnection, exception:bool=False)->dict:
    """
    Extract AnyLog dictionary
    :args:
        anylog_conn:AnyLogConnection - AnyLog REST connection information
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header
        anylog_dict:dict - results for dictionary
        r:bool, error:str - whether the command failed & why
    :return:

    """
    anylog_dict = {}
    headers = {
        'command': 'get dictionary where format=json',
        'User-Agent': 'AnyLog/1.23'
    }
    r, error = anylog_conn.get(headers=headers)

    if r is False or int(r.status_code) != 200:
        if exception is True:
            support.print_rest_error(error_type='GET', cmd=headers['command'], error=error)
    else:
        try:
            anylog_dict = r.json()
        except Exception as json_error:
            try:
                anylog_dict = r.text
            except Exception as txt_error:
                print(f'Failed to extract results for `{headers["cmd"]}` (JSON Error: {json_error} | Text Error: {txt_error})')

    return anylog_dict


def get_processes(anylog_conn:AnyLogConnection, exception:bool=False)->dict:
    """
    Extract AnyLog processes
    :args:
        anylog_conn:AnyLogConnection - AnyLog REST connection information
        exception:bool - whether to print exceptions
    :params:
        status:bool
        processes_dict - dict of AnyLog processes
        r:bool, error:str - whether the command failed & why
    :return:
        processes_dict
    """
    processes_dict = {}
    headers = {
        'command': 'get processes where format=json',
        'User-Agent': 'AnyLog/1.23'
    }
    r, error = anylog_conn.get(headers=headers)

    if r is False or int(r.status_code) != 200:
        if exception is True:
            support.print_rest_error(error_type='GET', cmd=headers['command'], error=error)
    else:
        try:
            processes_dict = r.json()
        except Exception as json_error:
            try:
                processes_dict = r.text
            except Exception as txt_error:
                print(f'Failed to extract results for `{headers["cmd"]}` (JSON Error: {json_error} | Text Error: {txt_error})')

    return processes_dict


def get_hostname(anylog_conn:AnyLogConnection, exception:bool=False)->str:
    hostname = ""
    headers = {
        'command': 'get hostname',
        'User-Agent': 'AnyLog/1.23'
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        support.print_error(error_type='GET', cmd=headers['command'], error=error)
    else:
        try:
            hostname = r.text
        except Exception as e:
            if exception is True:
                print(f'Failed to return hostname against {anylog_conn.conn} (Error: {e})')
    return hostname
