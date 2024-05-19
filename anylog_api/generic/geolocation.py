"""
The following module provides the ability to get geolocation of a node via REST

Sample Geolocation
{
    'ip' : '73.202.144.172',
    'hostname' : 'c-73-202-142-172.hsd1.ca.comcast.net',
    'city' : 'San Jose',
    'region' : 'California',
    'country' : 'US',
    'loc' : '37.2560,-121.8939',
    'org' : 'AS7922 Comcast Cable Communications, LLC',
    'postal' : '95125',
    'timezone' : 'America/Los_Angeles',
    'readme' : 'https://ipinfo.io/missingauth'
} 
"""
import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.generic.get import get_dictionary
from anylog_api.anylog_connector_support import execute_publish_cmd


def set_location(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False):
    """
    using ipinfo.io get geolocation of your node and store it locally as a variable (geolocation)
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status;bool - command status
        headers:dict - REST headers
    :return:
        None - if not executed
        True - if success
        False - if fails
    """
    status = None
    headers = {
        'command': 'geolocation = rest get where url=https://ipinfo.io/json',
        'User-Agent': 'AnyLog/1.23'
    }

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    elif return_cmd is True:
        return headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def extract_geolocation(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                        return_cmd:bool=False, exception:bool=False):
    """
    using `get_dictionary` function extract geolocation values
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        output:dict - result set
        dictionary_values:dict - dictionary from node
    :return:
        output consisting of geolocation
    """
    output = {}
    dictionary_values = get_dictionary(conn=conn, json_format=True, destination=destination, view_help=view_help,
                                       return_cmd=return_cmd, exception=exception)

    if 'geolocation' in dictionary_values and isinstance(dictionary_values):
        output = dictionary_values['geolocation']
    elif return_cmd is True:
        output = dictionary_values

    return output


def get_geolocation(conn:anylog_connector.AnyLogConnector, destination:str=None,
                    view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    main to get geolocation
    :steps:
        1. set location
        2. get location
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status:bool
        output:dict - result set
    :return:
        if return_cmd is True
            -> status -  query for set_location
            -> output -  query for extract_geolocation
        else
            -> output
    """

    status = set_location(conn=conn, destination=destination, view_help=view_help, return_cmd=return_cmd,
                          exception=exception)
    if True in [status, return_cmd, view_help]:
        output = extract_geolocation(conn=conn, destination=destination, view_help=view_help, return_cmd=return_cmd,
                                     exception=exception)
    if return_cmd is True:
        return status, output
    
    return output