"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import json
import re


def json_dumps(content, indent:int=0, exception:bool=False)->str:
    """
    Convert dictionary into serialized JSON
    :args:
        content - content to convert into dictionary
        indent:int - JSON indent
        exception:bool - whether to print exception
    :params:
        output - content as dictionary form
    :return:
        output
        if fails - raise JSON error
    """
    output = None
    try:
        if indent > 0:
            output = json.dumps(content, indent=indent)
        else:
            output = json.dumps(content)
    except Exception as error:
        if exception is True:
            raise json.JSONDecodeError(msg=f"Failed to convert content into serialized JSON format (Error: {error})",
                                       doc=str(content), pos=0)

    return output


def check_conn_info(conn:str)->bool:
    """
    Check whether connection is correct format
    :args:
        conn:str - REST connection IP:Port
    :params:
        pattern:str - pattern to check connection is correct format
    :return:
        if fails then raise an error
        else - True
    """
    pattern1 = r'^(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])' \
              r'(?:\.(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])){3}:\d{1,5}$'
    pattern2 = f'^(?:[a-zA-Z0-9._%+-]+(?::[a-zA-Z0-9._%+-]+)?@)?{pattern1}'

    if not re.match(pattern1, conn) and not re.match(pattern2, conn):
        raise ValueError('Connection information not in correct format - example [IP_Address]:[ANYLOG_REST_PORT]')

    return True


def separate_conn_info(conn:str)->(str, tuple):
    """
    Separate connection information provided
    :args:
        conn:str - REST connection information
    :params:
        pattern:str - pattern information
        auth:tuple - authentication information
    :return:
        conn, auth
    """
    auth = None
    if check_conn_info(conn=conn) is True and '@' in conn:
        auth, conn = conn.split('@')
        auth = tuple(auth.split(":"))

    return conn, auth


def validate_conn_info(conn:str):
    if not conn:
        raise ValueError('Missing connection information, cannot continue....')
    conns_list = {conn_info: None for conn_info in conn.split(",")}
    if not all(check_conn_info(conn) for conn in list(conns_list.keys())):
        raise ValueError('One or more set of connections has invalid format')
    return conns_list

