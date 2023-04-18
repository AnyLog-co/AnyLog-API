import anylog_connector


def post_cmd(anylog_conn:anylog_connector.AnyLogConnector, command:str, view_help:bool=False):
    """
    execute a generic POST command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - Connection to AnyLog node
        cmd:str - command to execute
        view_help:bool - execute `help` against `get status`
    :params:
        status:bool
        headers:dict - REST header information
    :return:
        True -  if request was a success
        False - if request failed
        None -  if viewed help
    """
    status = True
    headers = {
        "command": command,
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(anylog_conn=anylog_conn, cmd=headers['command'])
        return None

    r = anylog_conn.post(headers=headers)
    if int(r.status_code) != 200:
        status = False
    return status


def set_license_key(anylog_conn:anylog_connector.AnyLogConnector, license_key:str, view_help:bool=False):
    """
    Set license key
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#set-command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog
        license_key:str - license key
        view_help:bool - execute `help` against `set license`
    :params:
        status:bool
        headers:dict - REST header information
        r:requests.model.Response - response from REST request
    :return:
        None - if help
        False - if fails
        True - if succeed
    """
    status = True
    headers = {
        "command": f"set license where activation_key = {license_key}",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(anylog_conn=anylog_conn, cmd=headers['command'])
        return None

    r = anylog_conn.post(headers=headers)
    if r is None or int(r.status_code) != 200:
        status = False

    return status


def set_schedule1(anylog_conn:anylog_connector.AnyLogConnector, view_help:bool=False):
    """
    Execute `run scheduler 1` command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/alerts%20and%20monitoring.md#invoking-a-scheduler
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog
        view_help:bool - execute `help` against `set license`
    :params:
        status:bool
        headers:dict - REST header information
        r:requests.model.Response - response from REST request
    :return:
        None - if help
        False - if fails
        True - if succeed
    """
    status = True
    status = True
    headers = {
        "command": "run scheduler 1",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(anylog_conn=anylog_conn, cmd=headers['command'])
        return None

    r = anylog_conn.post(headers=headers)
    if r is None or int(r.status_code) != 200:
        status = False

    return status


def run_mqtt_client(anylog_conn:anylog_connector.AnyLogConnector, broker:str, port:str, user:str=None, password:str=None,
                    log:bool=False, topic_name:str='*', db_name:str=None, table_name:str=None, params:dict={},
                    view_help:bool=False):
    status = True
    headers = {
        "command": f"run mqtt client where broker={broker} and port={port}",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(anylog_conn=anylog_conn, cmd=headers['command'])
    if broker == "rest":
        headers["command"] += " and user-agent=anylog"
    if user is not None:
        headers["command"] += f" and user={user}"
    if password is not None:
        headers["command"] += f" and password={password}"
    if log is True:
        headers["command"] += f" and log=true"
    else:
        headers["command"] += f" and log=false"

    headers["command"] += f" and topic=(name={topic_name}"
    if db_name is not None and table_name is not None:
        headers["command"] += f" and dbms={db_name} and table={table_name}"
        for key in params:
            if params[key]["type"] == "timestamp":
                if "bring" in params[key]["value"]:
                    headers["command"] += f' and column.{key}.timestamp=\"{params[key]["value"]}\"'
                else:
                    headers["command"] += f' and column.{key}.timestamp={params[key]["value"]}'
            else:
                headers["command"] += f' and column.{key}=(type={params[key]["type"]} and value=\"{params[key]["value"]}\")'

    headers["command"] += ")"

    r = anylog_conn.post(headers=headers)
    if r is None or int(r.status_code) != 200:
        status = False

    return status


def publish_data(anylog_conn:anylog_connector.AnyLogConnector, topic:str, payload:str):
    """
    Publish data into AnyLog
    :args:
    """
    status = True
    headers = {
        'command': 'data',
        'topic': topic,
        'User-Agent': 'AnyLog/1.23',
        'Content-Type': 'text/plain'
    }

    r = anylog_conn.post(headers=headers, payload=payload)
    if r is None or int(r.status_code) != 200:
        status = False

    return status



