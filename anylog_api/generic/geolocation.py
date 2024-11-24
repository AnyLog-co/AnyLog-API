"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
from typing import Union
from xmlrpc.client import Error

from Cython.Build.Cythonize import parse_args

import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_dictionary
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.__support__ import check_ip, json_loads

GEO_URL = "https://ipinfo.io/json"

def publish_location(conn:anylog_connector.AnyLogConnector, ip_addr:str=None, destination:str=None,
                     view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[bool, str]:
    headers = {
        "command": f"loc_info = rest get where url = {GEO_URL}",
        "User-Agent": "AnyLog/1.23"
    }

    if ip_addr and check_ip(conn=ip_addr) is True:
        headers['command'] = headers['command'].replace(GEO_URL, f'https://ipinfo.io/{ip_addr}json')
    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)

    if return_cmd is True:
        status = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return status


def get_location(conn:anylog_connector.AnyLogConnector, ip_addr:str=None, destination:str=None,
                 view_help:bool=False, return_cmd:bool=False, exception:bool=False)->dict:
    """
    Get Geolocation for the node - this is used when declaring a policy -
    :global:
        GEO_URL:str - URL path to get location
    :url-output:
        {
              "ip": "45.33.73.224",
              "hostname": "45-33-73-224.ip.linodeusercontent.com",
              "city": "Cedar Knolls",
              "region": "New Jersey",
              "country": "US",
              "loc": "40.8220,-74.4488",
              "org": "AS63949 Akamai Connected Cloud",
              "postal": "07927",
              "timezone": "America/New_York",
              "readme": "https://ipinfo.io/missingauth"
        }
    :args:
        conn:anylog_connector.AnyLogConnector - Connection to AnyLog
        ip:str - IP address
        view_help:bool - print help information
        return_cmd:bool - return command to be executed
        exception:bool - print exception
    :params;
        location:dict - node location
        headers:dict - REST headers
    :return:
        if return_cmd then returns the command
        location
    :url-input:
        {
              "ip": "45.33.73.224",
              "hostname": "45-33-73-224.ip.linodeusercontent.com",
              "city": "Cedar Knolls",
              "region": "New Jersey",
              "country": "US",
              "loc": "40.8220,-74.4488",
              "org": "AS63949 Akamai Connected Cloud",
              "postal": "07927",
              "timezone": "America/New_York",
              "readme": "https://ipinfo.io/missingauth"
        }
    :output:
        {
              "city": "Cedar Knolls",
              "city": "New Jersey",
              "country": "US",
              "loc": "40.8220,-74.4488",
        }
    """
    location = {}

    status = publish_location(conn=conn, ip_addr=ip_addr, destination=destination, view_help=view_help,
                              return_cmd=return_cmd, exception=exception)

    if status is False:
        if exception is True:
            raise Error(f'Failed to get location for the node using {GEO_URL}')
    else:
        geolocation = get_dictionary(conn=conn, variable='loc_info', json_format=True, destination=None,
                                     view_help=view_help, return_cmd=return_cmd, exception=exception)

        if return_cmd is True:
            location = {
                "set location": status,
                "get location": geolocation
            }
        elif geolocation:
            if isinstance(geolocation, str):
                geolocation = json_loads(content=geolocation, exception=exception)
            for param in geolocation:
                if param in ['loc', 'country', 'region', 'city']:
                    if param == 'region':
                        location['state'] = geolocation[param]
                    else:
                        location[param] = param
        return  location


