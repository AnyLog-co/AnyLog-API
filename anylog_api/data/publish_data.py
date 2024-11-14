"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""


import anylog_api.anylog_connector as anylog_connector
from anylog_api.__support__ import add_conditions
from anylog_api.__support__ import json_dumps
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.generic.get import get_help


def put_data(conn:anylog_connector.AnyLogConnector, payload, db_name:str, table_name:str, mode:str='streaming',
             return_cmd:bool=False, exception:bool=False):
    """
    Insert data into EdgeLake / AnyLog via PUT
    :args:
        conn:anylog_connector.AnyLogConnector
        payload - dict or list of data to insert (will automatically serialize if not string)
        db_name:str - logical database to store data in
        table_name:str - table to store data in (within logical database)
        mode:bool - whether to send data using streaming of file
        return_cmd:bool - return header information
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        serialize_data - serialized data
    :return:
        if return_cmd is True --> headers
        True -->  data sent
        False --> Fails to send data
    """
    headers = {
        'command': 'data',
        'dbms': db_name,
        'table': table_name,
        'mode': mode,
        'User-Agent': 'AnyLog/1.23',
        'Content-Type': 'text/plain'
    }

    if mode not in ['streaming', 'file']:
        headers['mode'] = 'streaming'
        if exception is True:
            print(f"Warning: Invalid mode format {mode}. Options: streaming (default), file ")

    serialize_data = json_dumps(payload)

    if return_cmd is True:
        status = headers
    else:
        status = execute_publish_cmd(conn=conn, cmd='PUT', headers=headers, payload=serialize_data, exception=exception)

    return status


def post_data(conn:anylog_connector.AnyLogConnector, payload, topic:str, return_cmd:bool=False, exception:bool=False):
    """
    Insert data into EdgeLake / AnyLog via POST
    :args:
        conn:anylog_connector.AnyLogConnector
        payload - dict or list of data to insert (will automatically serialize if list or dict)
        topic:str - msg client topic
        return_cmd:bool - return header information
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        serialize_data - serialized data
    :return:
        if return_cmd is True --> headers
        True -->  data sent
        False --> Fails to send data
    """
    headers = {
        'command': 'data',
        'topic': topic,
        'User-Agent': 'AnyLog/1.23',
        'Content-Type': 'text/plain'
    }

    if isinstance(payload, list):
        serialize_data = [json_dumps(row) for row in payload]
    elif isinstance(payload, dict):
        serialize_data = json_dumps(payload)
    else:
        serialize_data = payload

    if return_cmd is True:
        status = headers
    else:
        status = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=serialize_data, exception=exception)

    return status


def run_msg_client(conn:anylog_connector.AnyLogConnector, broker:str, topic:str, port:int=None, username:str=None,
                   password:str=None, log:bool=False, policy_id:str=None, db_name:str=None, table_name:str=None,
                   values:dict={}, is_rest_broker:bool=False, destination:str=None, view_help:bool=False,
                   return_cmd:bool=False, exception:bool=False):
    """
    Enable message client for POST, MQTT, Kafka
    :args:
        conn:anylog_connector.AnyLogConnector
        broker:str - broker
        topic:str - topic name
        port:int - port associated with broker value
        username:str - user associated with broker
        password:str - password associated with user
        log:bool - whether to enable logging or not

        policy_id:str - policy to be used with message client
        - OR -
        db_name:str - logical database name to be used with message client
        table_name:str - physical table to be used with message client
        values:dict - mapping information  Describe:
            {
                "timestamp": {"type": "timestamp", "value": "now()"},
                "col1": {"type": "float", "value": "bring [col1]", "optional": 'true', 'default': 3},
                "col2": {"type": "string", "value": "bring [col2]", "optional": 'true', 'default': 'a'}
           }

        destination:str - Remote destination
        view_help:bool - view help
        return_cmd:bool - return header information
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
    :return:
        if return_cmd is True --> headers
        True -->  data sent
        False --> Fails to send data
    """
    status = None
    headers = {
        "command": f'run msg client where broker={broker}',
        "User-Agent": 'AnyLog/1.23'
    }

    if port:
        headers["command"] += f" and port={port}"
    if is_rest_broker is True:
        headers["command"] += " and user-agent=anylog"
    if username:
        headers["command"] += f" and user={username}"
    if password:
        headers["command"] += f" and password={password}"
    if log is True:
        headers["command"] += " and log=true"
    else:
        headers["command"] += " and log=false"
    headers["command"] += f" and topic={topic}"

    if db_name or table_name or values:
        headers["command"] = headers["command"].replace(f"topic={topic}", f"topic=(name={topic}")
        if db_name:
            headers['command'] += f" and dbms={db_name}"
        if table_name:
            headers['command'] += f" and table={table_name}"
        if values:
            for key, values_dict in values.items():
                headers['command'] += " and "
                if 'value' in values_dict and 'bring' in values_dict['value']:
                    values_dict['value'] = '"' + values_dict['value'] + "'"
                if 'type' in values_dict and values_dict['type'].lower() == 'timestamp':
                    if 'value' not in values_dict:
                        headers['command'] += f"column.{key.replace(' ', '_').replace('-', '_')}.timestamp=now()"
                    else:
                        headers['command'] += f"column.{key.replace(' ', '_').replace('-', '_')}.timestamp={values_dict['value']}"
                elif 'value' in values_dict:
                    if 'type' not in values_dict or values_dict['type'].lower() not in ['string', 'int', 'float',
                                                                                        'bool', 'timestamp']:
                        headers['command'] += f"column.{key.replace(' ', '_').replace('-', '_')}=(type=string and value={values_dict['value']})"
                    else:
                        key = key.replace(' ', '_').replace('-', '_')
                        value = values_dict["value"].replace('"', '').replace("'","")
                        headers['command'] += f'column.{key}=(type={values_dict["type"].lower()} and value="{value}")'
        headers['command'] += ")"

    if destination:
        headers['destination'] = destination

    if view_help is True:
        headers['command'] = headers['command'].split('<')[-1].split('>')[0].replace("\n","").replace("\t", " ")
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        headers['command'] = headers['command'].split('<')[-1].split('>')[0].replace("\n", "").replace("\t", " ")
        status = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)

    return status


def get_msg_client(conn:anylog_connector.AnyLogConnector, client_id:int=None, destination:str=None,
                   view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    get message client information
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        client_id:int - Message client ID
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        output - content returned
        headers:dict - REST headers
    :return:
        if return_cmd == True -- command to execute
        if view_help == True - None
        results for query
    """
    output = None
    headers = {
        "command": "get msg client",
        "User-Agent": "AnyLog/1.23"
    }

    add_conditions(headers, id=client_id)

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers,  exception=exception)

    return output


def exit_msg_client(conn:anylog_connector.AnyLogConnector, client_id:int=None, destination:str=None,
                   view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    disconnect from msg client - if ID is set, exit specific client
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        client_id:int - Message client ID
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        status:bool
        headers:dict - REST headers
    :return:
        if return_cmd == True -- command to execute
        if view_help == True - None
        if execution succeeds - True
        if execution fails - False
    """
    status = None
    headers = {
        "command": "exit mqtt",
        "User-Agent": "AnyLog/1.23"
    }

    if client_id is not None:
        headers['command'] += f" {client_id}"
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


