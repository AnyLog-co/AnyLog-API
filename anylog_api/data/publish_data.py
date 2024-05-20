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
    status = None
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

    if not all(isinstance(payload, x) for x in [dict, list]):
        serialize_data = payload
    else:
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
    status = None
    headers = {
        'command': 'data',
        'topic': topic,
        'User-Agent': 'AnyLog/1.23',
        'Content-Type': 'text/plain'
    }

    if not all(isinstance(payload, x) for x in [dict, list]):
        serialize_data = payload
    else:
        serialize_data = json_dumps(payload)

    if return_cmd is True:
        status = headers
    else:
        status = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=serialize_data, exception=exception)

    return status


def run_msg_client(conn:anylog_connector.AnyLogConnector, broker:str, topic:str, port:int=None, username:str=None,
                   password:str=None, log:bool=False, policy_id:str=None, db_name:str=None, table_name:str=None,
                   values:dict={}, destination:str=None, view_help:bool=False, return_cmd:bool=False,
                   exception:bool=False):
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
        "command": 'run msg client',
        "User-Agent": 'AnyLog/1.23'
    }

    topic_info = f"(name={topic}"
    if policy_id:
        topic_info += f" and policy={policy_id})"
    else:
        if db_name:
            topic_info += f" and dbms={db_name}"
        if table_name:
            topic_info += f" and table={table_name}"
        if values:
            for key, values_dict in values.items():
                if 'value' not in values_dict or 'type' not in values_dict:
                    continue
                elif values_dict['type'] == 'timestamp':
                    cmd += f"\n\tcolumn.{key}.timestamp={values_dict["value"]} and"
                    if "bring" in values_dict["value"]:
                        cmd = cmd.replace(values_dict["value"], f'"{values_dict["value"]}"')
                else:
                    if values_dict['type'] not in ['string', 'int', 'float', 'bool', 'timestamp']:
                        values_dict['type'] = 'string'
                    cmd += f"\n\tcolumn.{key.replce(' ', '_')}=("
                    for param, param_value in values_dict.items():
                        cmd += f"{param}={param_value} and "
                        if isinstance(param_value, str) and "bring" in param_value:
                            cmd = cmd.replace(param_value, f'"{param_value}"')
                        elif param == 'default' and isinstance(param_value, str):
                            cmd = cmd.replace(f"{param}={param_value}", f'{param}="{param_value}"')
                        elif isinstance(param_value, bool) and param is True:
                            cmd = cmd.replace(param_value, f'true')
                        elif isinstance(param_value, bool) and param is False:
                            cmd = cmd.replace(param_value, f'false')
            cmd += ")"

    add_conditions(headers, broker=broker, port=port, username=username, password=password, log=log, topic=topic)

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


def run_operator(conn:anylog_connector.AnyLogConnector, operator_id:str, create_table:bool=True,
                 update_tsd_info:bool=True, archive_json:bool=True, compress_json:bool=True, archive_sql:bool=False,
                 compress_sql:bool=True, ledger_conn='!ledger_conn', threads:int=3, destination:str=None,
                 view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Enable operator process
    :args:
        conn:AnyLogConnector - connection to AnyLog
        operator_id:str - (policy) ID of the operator policy
        create_table:bool - A True value creates a table if the table doesn't exist.
        update_tsd_info - True/False to update a summary table (tsd_info table in almgm dbms) with status of files ingested.
        compress_json - True/False to enable/disable compression of the JSON file.
        compress_sql - True/False to enable/disable compression of the SQL file.
        archive_json:bool - True/False to move JSON files to archive.
        archive_sql:bool - True/False to move SQL files to archive.
        threads:int - number of operator threads
        ledger_conn - The IP and Port of a Master Node (if a master node is used)
        destination;str - Remote destination command
        return_cmd:bool - return command
        view_help:bool - whether to print info about command
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
        'command': f"run operator",
        'User-Agent': 'AnyLog/1.23'
    }

    add_conditions(headers, create_table=create_table, update_tsd_info=update_tsd_info, compress_json=compress_json,
                   compress_sql=compress_sql, archive_json=archive_json, archive_sql=archive_sql, master_node=ledger_conn,
                   policy=operator_id, threads=threads)

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


def run_publisher(conn:anylog_connector.AnyLogConnector, compress_file:bool=True, ledger_conn='!ledger_conn',
                  dbms_file_location:str='file_name[0]', table_file_location='file_name[1]', destination:str=None,
                  view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Enable publisher process
    :args:
        conn:AnyLogConnector - connection to AnyLog
        compress_file:bool - True/False to enable/disable compression of the JSON/SQL file.
        ledger_conn - The IP and Port of a Master Node (if a master node is used)
        dbms_file_location:str - where to set db name in file path
        table_file_location:str - where to set table name in file path
        destination;str - Remote destination command
        return_cmd:bool - return command
        view_help:bool - whether to print info about command
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
        'command': f"run publisher",
        'User-Agent': 'AnyLog/1.23'
    }

    add_conditions(headers, compress_json=compress_file, compress_sql=compress_file, master_node=ledger_conn,
                   dbms_name=dbms_file_location, table_name=table_file_location)

    if destination:
        headers['destination'] = destination

    if view_help is True:
        headers['command'] = headers['command'].split('<')[-1].split('>')[0].replace("\n", "").replace("\t", " ")
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


def get_operator(conn:anylog_connector.AnyLogConnector, json_format:bool=False, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False):
    """
    get operator
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        json_format:bool - Set `get operator` output in JSON format
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
        "command": "get operator",
        "User-Agent": "AnyLog/1.23"
    }
    if json_format is True:
        headers['command'] += " where format=json"
    if destination is not None:
        headers['destination'] = destination


    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers,  exception=exception)

    return output


def get_publisher(conn:anylog_connector.AnyLogConnector, json_format:bool=False, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False):
    """
    get publisher
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        json_format:bool - Set `get operator` output in JSON format
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
        "command": "get publisher",
        "User-Agent": "AnyLog/1.23"
    }
    if json_format is True:
        headers['command'] += " where format=json"
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
        output = headers['command']
    elif view_help is False:
        status = execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def exit_operator(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                  return_cmd:bool=False, exception:bool=False):
    """
    disconnect operator
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
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
        "command": "exit operator",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def exit_publisher(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                   return_cmd:bool=False, exception:bool=False):
    """
    disconnect publisher
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
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
        "command": "exit publisher",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status
