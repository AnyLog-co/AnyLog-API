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
    location = {}
    try:
        r = requests.get(url='https://ipinfo.io/json')
    except Exception as e:
        if exception is True:
            print(f"Failed to execute GET against 'https://ipinfo.io/json' (Error {e})")
    else:
        try:
            location = r.json()
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
        print_error(error_type='GET', cmd=headers['command'], error=error)
    elif 'running' in r.text and 'not' not in r.text:
        status = True
    return status


def get_hostname(anylog_conn:AnyLogConnection, exception:bool=False)->str:
    hostname = ""
    headers = {
        'command': 'get hostname',
        'User-Agent': 'AnyLog/1.23'
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(error_type='GET', cmd=headers['command'], error=error)
    else:
        try:
            hostname = r.text
        except Exception as e:
            if exception is True:
                print(f'Failed to return hostname against {anylog_conn.conn} (Error: {e})')
    return hostname


def get_dictionary(anylog_conn:AnyLogConnection, exception:bool=False)->dict:
    """
    Extract existing AnyLog dictionary
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        anylog_dictionary:dict - content in dictionary
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        anylog_dictionary
    """
    anylog_dictionary = {}
    headers = {
        'command': 'get dictionary where format=json',
        'User-Agent': 'AnyLog/1.23'
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(error_type='GET', cmd=headers['command'], error=error)
    else:
        try:
            anylog_dictionary =  r.json()
        except Exception as e:
            try:
                anylog_dictionary = r.text
            except Exception as e:
                if exception is True:
                    print(f'Failed to return dictionary results against {anylog_conn.conn} (Error: {e})')
    return anylog_dictionary


def get_hostname(anylog_conn:AnyLogConnection, exception:bool=False)->str:
    """
    Extract Hostname
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        hostname:str - machine hostname
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        hostname
    """
    hostname = ''
    headers = {
        'command': 'get hostname',
        'User-Agent': 'AnyLog/1.23'
    }
    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(error_type='GET', cmd=headers['command'], error=error)
    else:
        try:
            hostname = r.text
        except Exception as e:
            if exception is True:
                print(f'Failed to return dictionary results against {anylog_conn.conn} (Error: {e})')
    return hostname



