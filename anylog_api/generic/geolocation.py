"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_dictionary
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.__support__ import json_loads


GEO_URL = "https://ipinfo.io/json"


def get_location(conn:anylog_connector.AnyLogConnector, params:dict, destination:str=None, view_help:bool=False, return_cmd:bool=False,
                 exception:bool=False):
    """
    Get Geolocation for the node - this is used when declaring a policy -
    :global:
        GEO_URL:str - URL path to get location
    :args:
        conn:anylog_connector.AnyLogConnector - Connection to AnyLog
        params:dict - node configurations
        view_help:bool - print help information
        return_cmd:bool - return command to be executed
        exception:bool - print exception
    :params;
        location:dict - node location
        headers:dict - REST headers
    :return:
        if return_cmd then returns the command
        location
    """
    location = {}
    headers = {
        "command": f"loc_info = rest get where url = {GEO_URL}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']

    if 'loc_info' in params: # someone / something already ran the curl request on the node
        location = params['loc_info']
    elif location == {}: # configurations form params (if exist)
        if 'location' in params:
            location['loc'] = params['location']
        if 'country' in params:
            location['country'] = params['country']
        if 'state' in params:
            location['state'] = params['state']
        if 'city' in params:
            location['city'] = params['city']

    if location == {}: # if location still DNE then run locally
        output = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)
        if output is True:
            anylog_params =  get_dictionary(conn=conn, json_format=True, destination=None, view_help=view_help,
                                            return_cmd=return_cmd, exception=exception)
            if 'loc_info' in anylog_params:
                location = anylog_params['loc_info']

    if isinstance(location, str):
        dict_location = json_loads(location.replace("'",'"'), exception=exception)
        if dict_location is not None:
            location = dict_location
    for param in ['region', 'ip', 'hostname', 'org', 'postal', 'timezone', 'readme']:
        if param == 'region' and param in location:
            location['state'] = location['region']
        if param in location:
            del location[param]

    return location



