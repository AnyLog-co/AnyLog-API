"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import warnings

import anylog_api.anylog_connector as anylog_connector
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
            warnings.warn(f"Warning: Invalid mode format {mode}. Options: streaming (default), file ")

    serialize_data = json_dumps(content=payload, exception=exception)

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
        serialize_data = [json_dumps(content=row, exception=exception) for row in payload]
    elif isinstance(payload, dict):
        serialize_data = json_dumps(content=payload, exception=exception)
    else:
        serialize_data = payload

    if return_cmd is True:
        status = headers
    else:
        status = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=serialize_data, exception=exception)

    return status


def run_msg_client(conn:anylog_connector.AnyLogConnector, broker:str, topic:str, port:int=None,
                   is_rest_broker:bool=False, username:str=None, password:str=None, log:bool=False,
                   policy_id:str=None, db_name:str=None, table_name:str=None, values:dict=None, destination:str=None,
                   view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Enable message client for POST, MQTT, Kafka
    :args:
        conn:anylog_connector.AnyLogConnector
        broker:str - broker
        topic:str - topic name
        port:int - port associated with broker value
        is_rest_broker:bool - whether REST (POST)s connection for message client
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
    headers = {
        "command": f'run msg client where broker={broker} and ',
        "User-Agent": 'AnyLog/1.23'
    }

    if port:
        headers['command'] += f" port={port} and"
    if is_rest_broker is True:
        headers['command'] += f" user-agent=anylog"
    if username:
        headers['command'] += f" user={username} and"
    if password:
        headers['command'] += f" password={password} and"
    if isinstance(log, bool) or str(log).lower() in ['true', 'false']:
        headers['command'] += f" log={str(log).lower()} and"
    else:
        headers['command'] += f" log=false and"
        if exception is True:
            warnings.warn(f"Warning: Invalid message client log value, setting value to default - `false`")

    complete_topic = f"topic=*"
    if topic and policy_id:
        complete_topic=f"topic=(name={topic} and policy={policy_id})"
    elif topic:
        complete_topic = f"topic=(name={topic} and"
        if db_name or table_name or values:
            if db_name:
                complete_topic += f" db_name={db_name} and"
            if table_name:
                complete_topic += f" table={table_name} and"
            if values:
                for key in values:
                    column_name = key.lower().strip().replace(" ", "_")
                    value = None
                    value_type = 'string'
                    if 'value' in values[key]:
                        value = values[key]["value"].strip()
                    if 'type' in values[key] and values[key].strip().lower() in ['int', 'float', 'bool', 'string']:
                        value_type = values[key].strip().lower()
                    elif exception is True:
                        warnings.warn('Invalid column value type, using `string` value (Default values: int, float, bool, string)')

                    if value_type == 'timestamp' and not value:
                        complete_topic += f"column.{column_name}.timestamp=now() and"
                    elif value_type == 'timestamp' and 'bring' in value.lower():
                        complete_topic += f'column.{column_name}.timestamp="{value}" and'
                    elif value_type == 'timestamp':
                        complete_topic += f'column.{column_name}.timestamp={value} and'
                    elif 'bring' in value.lower() or " " in value:
                        column_name += f'column.{column_name}=(type={value_type} and value="{value}") and'
                    elif value:
                        column_name += f'column.{column_name}=(type={value_type} and value={value}) and'
            complete_topic = complete_topic.rsplit(" and", 1)[0] + ")"
        else:
            complete_topic = f"topic={topic}"

    headers['command'] += complete_topic

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    else:
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
    headers = {
        "command": "get msg client",
        "User-Agent": "AnyLog/1.23"
    }


    if client_id:
        try:
            client_id = int(client_id)  # Raises ValueError if conversion fails
        except ValueError:
            if exception is True:
                warnings.warn('Invalid value type for client ID. Value must be an integer.')
        except KeyError as e:
            if exception is True:
                warnings.warn(f"Missing required key in headers: {e}")
        else:
            headers['command'] += f" WHERE id={client_id}"

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
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
    else:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


