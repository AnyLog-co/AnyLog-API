import anylog_connector


def post_cmd(anylog_conn:anylog_connector.AnyLogConnector, command:str, payload:str=None, destination:str=None,
             execute_cmd:bool=True, view_help:bool=False):
    """
    execute a generic POST command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - Connection to AnyLog node
        cmd:str - command to execute
        payload:str - content to send over POST
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - execute `help` against `get status`
    :params:
        status:bool
        headers:dict - REST header information
    :return:
        True -  if request was a success
        False - if request failed
        None -  if viewed help
    """
    headers = {
        "command": command,
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(anylog_conn=anylog_conn, cmd=headers['command'])
        return None
    elif execute_cmd is True:
        if destination is not None:
            headers["destination"] = destination
        r = anylog_conn.post(headers=headers, payload=payload)
        if r is None or int(r.status_code) != 200:
            return False
        return True

    return headers["command"]


def set_license_key(anylog_conn:anylog_connector.AnyLogConnector, license_key:str, execute_cmd:bool=True,
                    view_help:bool=False):
    """
    Set license key
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#set-command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog
        license_key:str - license key
        execute_cmd:bool - execute a given command, if False, then return command
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
    command = f"set license where activation_key = {license_key}",

    return post_cmd(anylog_conn=anylog_conn, cmd=command, payload=None, execute_cmd=execute_cmd, view_help=view_help)


def run_scheduler(anylog_conn:anylog_connector.AnyLogConnector, schedule_number:int=None, execute_cmd:bool=True,
                  view_help:bool=False):
    """
    Execute `run scheduler 1` command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/alerts%20and%20monitoring.md#invoking-a-scheduler
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog
        schedule_number:int - schedule number (ex `run schedule 1`
        execute_cmd:bool - execute a given command, if False, then return command
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
    command = "run scheduler"


    if schedule_number is not None:
        command += " " + str(schedule_number)

    return post_cmd(anylog_conn=anylog_conn, cmd=command, payload=None, execute_cmd=execute_cmd, view_help=view_help)


def declare_schedule(anylog_conn:anylog_connector.AnyLogConnector, time:str, task:str, start:str=None, name:str=None,
                     execute_cmd:bool=True, view_help:bool=False):
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
    command = f"schedule time={time}",

    if name is not None:
        command += f" and name={name}"
    if start is not None:
        command += f" and start={start}"
    command += f' task {task}'

    return post_cmd(anylog_conn=anylog_conn, cmd=command, payload=None, execute_cmd=execute_cmd, view_help=view_help)


def run_mqtt_client(anylog_conn:anylog_connector.AnyLogConnector, broker:str, port:str, user:str=None, password:str=None,
                    log:bool=False, topic_name:str='*', db_name:str=None, table_name:str=None, params:dict={},
                    execute_cmd:bool=True, view_help:bool=False):
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
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - execute `help` against `set license`
    :params:
        status:bool
        headers:dict - REST header information
        r:results.model.Response - request response
    :return:
        status
    """
    command = f"run mqtt client where broker={broker} and port={port}",

    if broker == "rest":
        command += " and user-agent=anylog"
    if user is not None:
        command += f" and user={user}"
    if password is not None:
        command += f" and password={password}"
    if log is True:
        command += f" and log=true"
    else:
        command += f" and log=false"

    command += f" and topic=(name={topic_name}"
    if db_name is not None and table_name is not None:
        command += f" and dbms={db_name} and table={table_name}"
        for key in params:
            if params[key]["type"] == "timestamp":
                if "bring" in params[key]["value"]:
                    command += f' and column.{key}.timestamp=\"{params[key]["value"]}\"'
                else:
                    command += f' and column.{key}.timestamp={params[key]["value"]}'
            else:
                command += f' and column.{key}=(type={params[key]["type"]} and value=\"{params[key]["value"]}\")'
    command += ")"

    return post_cmd(anylog_conn=anylog_conn, cmd=command, payload=None, execute_cmd=execute_cmd, view_help=view_help)





