import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.generic.post import execute_cmd


def __build_msg_client(broker:str, topic:str, port:int=None, username:str=None, password:str=None, log:bool=False,
                       policy_id:str=None, dbms:str=None, table:str=None, values:dict={})->str:
    """
    Build message client command
    :args:
        broker:str - broker
        topic:str - topic nmae
        port:int - port associated with broker value
        username:str - user associated with broker
        password:str - password associated with user
        log:bool - whether to enable logging or not
        policy_id:str - policy to be used with message client
        - OR -
        dbms:str - logical database name to be used with message client
        table:str - physical table to be used with message client
        values:dict - mapping information  Describe:
            {
                "timestamp": {"type": "timestamp", "value": "now()"},
                "col1": {"type": "float", "value": "bring [col1]", "optional": 'true', 'default': 3},
                "col2": {"type": "string", "value": "bring [col2]", "optional": 'true', 'default': 'a'}
           }
    :params:
        cmd:str - run msg client where cmd
    :return:
        cmd
    """
    cmd = f"<run msg client where broker={broker}"
    if port is not None:
        cmd += f" and port={port}"
    if username is not None:
        cmd += f" and username={username}"
    if password is not None:
        cmd += f" and passwword={password}"
    cmd += " and log=false"
    if log is True:
        cmd = cmd.replace("false", "true")
    cmd += f" and topic=(\n\tname={topic} and "
    if policy_id is not None:
        cmd += f"\n\tpolicy={policy_id}"
    else:
        if dbms is not None:
            cmd += f"\n\tdbms={dbms} and "
        if table is not None:
            cmd += f"\n\ttable={table} and"
        if values:
            for key, values_dict in values.items():
                if 'value' not in values_dict and 'type' not in values_dict:
                    continue
                if values_dict['type'] == 'timestamp':
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
                        elif isinstance(param_value, bool):
                            bools = {True: "true", False: "false"}
                            cmd = cmd.replace(param_value, f'"{bools["param_value"]}"')

                    cmd = cmd.rstrip(" and ") + ')'
            cmd = cmd.rstrip(" and")

    cmd += "\n)>"

    return cmd


def run_msg_client(conn:anylog_connector.AnyLogConnector, broker:str, topic:str, port:int=None, username:str=None,
                   password:str=None, log:bool=False, policy_id:str=None, dbms:str=None, table:str=None, values:dict={},
                   destination:str=None, view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    run message client
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        broker:str - broker
        topic:str - topic nmae
        port:int - port associated with broker value
        username:str - user associated with broker
        password:str - password associated with user
        log:bool - whether to enable logging or not
        policy_id:str - policy to be used with message client
        - OR -
        dbms:str - logical database name to be used with message client
        table:str - physical table to be used with message client
        values:dict - mapping information  Describe:
            {
                "timestamp": {"type": "timestamp", "value": "now()"},
                "col1": {"type": "float", "value": "bring [col1]", "optional": 'true', 'default': 3},
                "col2": {"type": "string", "value": "bring [col2]", "optional": 'true', 'default': 'a'}
           }
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
    # publish cmd
    headers = {
        "command": __build_msg_client(broker=broker, port=port, username=username, password=password, log=log,
                                      topic=topic, dbms=dbms, table=table, policy_id=policy_id, values=values),
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    elif return_cmd is True:
        return headers['command']
    else:
        status = execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

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
        status:bool
        headers:dict - REST headers
    :return:
        if return_cmd == True -- command to execute
        if view_help == True - None
        if execution succeeds - True
        if execution fails - False
    """
    status = None
    # publish cmd
    headers = {
        "command": "get msg client",
        "User-Agent": "AnyLog/1.23"
    }
    if client_id is not None:
        headers['commmand'] += f" {client_id}"
    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    elif return_cmd is True:
        return headers['command']
    else:
        status = execute_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status