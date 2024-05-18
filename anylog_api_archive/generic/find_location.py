import ast

from anylog_api.anylog_connector import AnyLogConnector
import anylog_api.generic.get as generic_get
import anylog_api.generic.post as generic_post


def __set_location(conn:AnyLogConnector, destination:str=None, view_help:bool=False, return_cmd:bool=False,
                   exception:bool=False)->bool:
    """
    Using `https://ipinfo.io/json` store location of node on node
    :sample:
    Content being generated when executing https://ipinfo.io/json
        {
         "ip": "24.23.250.144",
         "hostname": "c-24-23-250-144.hsd1.ca.comcast.net",
         "city": "San Mateo",
         "state": "California",
         "country": "US",
         "loc": "37.5630,-122.3255",
         "org": "AS33651 Comcast Cable Communications, LLC",
         "postal": "94401",
         "timezone": "America/Los_Angeles",
         "readme": "https://ipinfo.io/missingauth"
        }
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        status:bool
        headers:dict - REST header information
    :return:
        True if request was successful
        False if request failed
    """
    status = True
    headers = {
        'command': 'location_info = rest get where url=https://ipinfo.io/json',
        'User-Agent': 'AnyLog/1.23'
    }

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        generic_get.get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']
    else:
        status = generic_post.execute_cmd(conn=anylog_conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def __get_location(anylog_conn:AnyLogConnector, exception:bool=False)->(str, str, str, str):
    """
    Extract information from `location_info` AnyLog parameter
    :args:
    :params:
        configs:dict - AnyLog dictionary values
        location_configs:dict - formatted location information as dictionary from configs
        location:str - coordinates
        country:str
        state:str
        city:str
    :return:
        location, country, state, city
    """
    configs = generic_get.get_dictionary(anylog_conn=anylog_conn, json_format=True, view_help=False, exception=exception)
    location = None
    country = None
    state = None
    city = None

    try:
        location_configs = ast.literal_eval(configs['location_info'])
    except Exception as error:
        if exception is True:
            print(f'Failed to get location information from node. (Error: {error})')
    else:
        if 'loc' in location_configs:
            location = location_configs['loc']
        if 'country' in location_configs:
            country = location_configs['country']
        if 'state' in location_configs:
            state = location_configs['region']
        if 'city' in location_configs:
            city = location_configs['city']

    return location, country, state, city


def get_location(anylog_conn:AnyLogConnector, exception:bool=False)->dict:
    """
    Process to get location information
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        location:str - coordinates
        country:str
        state:str
        city:str
    :return:
        location, country, state, city
    """
    location = None
    country = None
    state = None
    city = None

    if __set_location(anylog_conn=anylog_conn, exception=exception) is True:
        location, country, state, city = __get_location(anylog_conn=anylog_conn, exception=exception)

    return {
        'location': location,
        'country': country,
        'state': state,
        'city': city
    }

