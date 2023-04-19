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


def run_scheduler(anylog_conn:anylog_connector.AnyLogConnector, schedule_number:int=None, view_help:bool=False):
    """
    Execute `run scheduler 1` command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/alerts%20and%20monitoring.md#invoking-a-scheduler
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog
        schedule_number:int - schedule number (ex `run schedule 1`
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
        "command": "run scheduler",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(anylog_conn=anylog_conn, cmd=headers['command'])
        return None

    if schedule_number is not None:
        headers["command"] += " " + str(schedule_number)

    r = anylog_conn.post(headers=headers)
    if r is None or int(r.status_code) != 200:
        status = False

    return status


def declare_schedule(anylog_conn:anylog_connector.AnyLogConnector, time:str, task:str, start:str=None, name:str=None,
                     view_help:bool=False):
    """
    Declare new scheduled process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/alerts%20and%20monitoring.md#adding-tasks-to-the-scheduler
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        time:str - how often to run the scheduled process
        task:str - process (cmd) to run
        start:str - Scheduled start time for first execution of the task. The default value is the current day and time.
        name:str - name of the scheduled task
        view_help:bool - whether to print help information
    :params:
        status:bool
        headers:dict - REST header information
        r:requests.model.Response - response from REST request
    :return:
        True - Success
        False - Fails
        None - print help
    :note:
        for schedule to start user needs to invoke it
    """
    status = None
    headers = {
        "command": f"schedule time={time}",
        "User-Agent": "AnyLog/1.23"
    }
    if view_help is True:
        anylog_connector.view_help(anylog_conn=anylog_conn, cmd=headers['command'])
        return None

    if name is not None:
        headers["command"] += f" and name={name}"
    if start is not None:
        headers["command"] += f" and start={start}"
    headers["command"] += f' task {task}'

    r = anylog_conn.post(headers=headers)
    if r is None or int(r.status_code) != 200:
        status = False

    return status


def run_mqtt_client(anylog_conn:anylog_connector.AnyLogConnector, broker:str, port:str, user:str=None, password:str=None,
                    log:bool=False, topic_name:str='*', db_name:str=None, table_name:str=None, params:dict={},
                    view_help:bool=False):
    """
    Execute `run mqtt client` command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog
        broker:str - broker IP
        port:str - broker port
        user:str - authentication user
        password:str - authentication password
        log:bool - whether to print MQTT client logs
        topic_name:str - topic to send data against
        db_name:str - logical databsae name
        table_name:str - logical table name
        params:dict - topic parameters (such as timestamp and value)
        view_help:bool - execute `help` against `set license`
    :params:
        status:bool
        headers:dict - REST header information
        r:results.model.Response - request response
    :return:
        status
    """
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





