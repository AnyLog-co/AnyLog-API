import requests
from anylog_connection import AnyLogConnection
from support import print_error


def get_location(exception:bool=False)->str:
    """
    Get location from  https://ipinfo.io/json
    :args:
        exception:bool - whether or not to print exception(s)
    :params:
        location:str - location from URL
        r:requests.models.Response- request response
    :return:
        location
    """
    location = '0.0, 0.0'
    try:
        r = requests.get(url='https://ipinfo.io/json')
    except Exception as e:
        if exception is True:
            print(f"Failed to execute GET against 'https://ipinfo.io/json' (Error {e})")
    else:
        try:
            location = r.json()['loc']
        except Exception as e:
            if exception is True:
                print(f'Failed to extract location (Error {e})')
    return location


def validate_status(anylog_conn:AnyLogConnection, exception:bool=False)->bool:
    """
    Validate if Node is running or not
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        status:bool
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        if success return True
        else False
    """
    status = False
    headers = {
        'command': 'get status',
        'User-Agent': 'AnyLog/1.23'
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(print_error='GET', cmd=headers['command'], error=error)
    elif 'running' in r.text and 'not' not in r.text:
        status = True
    return status


def get_dictionary(anylog_conn:AnyLogConnection, exception:bool=False)->dict:
    """
    Get dictionary in dictionary format
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        dictionary:dict - dictionary of values extracted from AnyLog
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        dictionary as dict
    """
    dictionary = {}
    headers = {
        "command": "get dictionary where format=json",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(print_error='GET', cmd=headers['command'], error=error)
    else:
        try:
            dictionary = r.json()
        except Exception as e:
            try:
                dictionary = r.text
            except Exception as e:
                if exception is True:
                    print(f"Failed to extract content for {headers['command']} (Error: {e})")
    return dictionary


def get_event_log(anylog_conn:AnyLogConnection, exception:bool=False)->dict:
    """
    Get event log in dictionary format
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        event_log:dict - event log extracted from AnyLog
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        dictionary as dict
    """
    event_log = {}
    headers = {
        "command": "get event log where format=json",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(print_error='GET', cmd=headers['command'], error=error)
    else:
        try:
            event_log = r.json()
        except Exception as e:
            try:
                event_log = r.text
            except Exception as e:
                if exception is True:
                    print(f"Failed to extract content for {headers['command']} (Error: {e})")
    return event_log


def get_error_log(anylog_conn:AnyLogConnection, exception:bool=False)->dict:
    """
    Get error log in dictionary format
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        error_log:dict - error log extracted from AnyLog
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        dictionary as dict
    """
    error_log = {}
    headers = {
        "command": "get error log where format=json",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(print_error='GET', cmd=headers['command'], error=error)
    else:
        try:
            error_log = r.json()
        except Exception as e:
            try:
                error_log = r.text
            except Exception as e:
                if exception is True:
                    print(f"Failed to extract content for {headers['command']} (Error: {e})")
    return error_log


def get_processes(anylog_conn:AnyLogConnection, exception:bool=False)->dict:
    """
    Get processes in dictionary format
    :command:
        get processes where format=json
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        get_process:dict - get processes as a dictionary
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        dictionary as dict
    """
    get_process = {}
    headers = {
        "command": "get processes where format=json",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(print_error='GET', cmd=headers['command'], error=error)
    else:
        try:
            get_process = r.json()
        except Exception as e:
            try:
                get_process = r.text
            except Exception as e:
                if exception is True:
                    print(f"Failed to extract content for {headers['command']} (Error: {e})")
    return get_process


def get_hostname(anylog_conn:AnyLogConnection, exception:bool=False)->str:
    """
    Extract hostname
    :command:
        get hostname
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        hostname:str - hostname
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        hostname
    """
    hostname = ''
    headers = {
        "command": "get hostname",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(print_error='GET', cmd=headers['command'], error=error)
    else:
        try:
            hostname = r.text
        except Exception as e:
            if exception is True:
                print(f'Failed to extract hostname (Error: {e})')

    return hostname
