import anylog_connector


def get_cmd(anylog_conn:anylog_connector.AnyLogConnector, command:str, destination:str=None, execute_cmd:bool=False,
            view_help:bool=False):
    """
    execute a generic GET command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - Connection to AnyLog node
        cmd:str - command to execute
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - execute `help` against `get status`
    :params:
        headers:dict - REST header information
    :return:
        output for GET request
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
        return anylog_conn.get(headers=headers)

    return headers["command"]


def get_status(anylog_conn:anylog_connector.AnyLogConnector, json_format:bool=True, destination:str=None,
               execute_cmd:bool=True, view_help:bool=False):
    """
    Check whether node is running or not
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-status-command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - Connection to AnyLog node
        json_format:bool - get result in JSON format
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - execute `help` against `get status`
    :params:
        status:bool
        headers:dict - REST header information
        output - REST result
    :return:
        True/False if command gets executed (True if running false if Fails)
        raw output if execute_cmd is False
    """
    command = "get status"

    if json_format is True:
        command += " where format=json"

    output = get_cmd(anylog_conn=anylog_conn, command=command, destination=destination, execute_cmd=execute_cmd,
                     view_help=view_help)

    if execute_cmd is True:
        status = False
        if json_format is True and "Status" in output and "running" in output["Status"] and "not" not in output["Status"]:
            status = True
        elif "running" in output and "not" not in output:
            status = True
        return status

    return output


def check_license(anylog_conn:anylog_connector.AnyLogConnector, destination:str=None, execute_cmd:bool=True,
                  view_help:bool=False):
    """
    Check whether license key is active or not
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#get-command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - Connection to AnyLog node
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - execute `help` against `get status`
    :params:
        status:bool
        headers:dict - REST header information
        output - REST result
    :return:
        None - help
        False - failed
        True - success
    """
    command = "get license"

    return get_cmd(anylog_conn=anylog_conn, command=command, destination=destination, execute_cmd=execute_cmd,
                   view_help=view_help)


def get_dictionary(anylog_conn:anylog_connector.AnyLogConnector, json_format:bool=True, destination:str=None,
                   execute_cmd:bool=True, view_help:bool=False):
    """
    Extract dictionary from AnyLog
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-dictionary-command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - Connection to AnyLog node
        json_format:bool - get result in JSON format
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - execute `help` against `get dictionary`
    :params:
        status:bool
        headers:dict - REST header information
    :return:
        AnyLog dictionary
    """
    status = False
    command = "get dictionary"

    return get_cmd(anylog_conn=anylog_conn, command=command, destination=destination, execute_cmd=execute_cmd,
                   view_help=view_help)


def get_processes(anylog_conn:anylog_connector.AnyLogConnector, json_format:bool=True, destination:str=None,
               execute_cmd:bool=True, view_help:bool=False):
    """
    View active processes in AnyLog
    :url:
         https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-processes-command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - Connection to AnyLog node
        json_format:bool - get result in JSON format
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - execute `help` against `get processes`
    :params:
        status:bool
        headers:dict - REST header information
    :return:
        AnyLog dictionary
    """
    command = "get processes"
    if json_format is True:
        command += " where format=json"

    return get_cmd(anylog_conn=anylog_conn, command=command, destination=destination, execute_cmd=execute_cmd,
                   view_help=view_help)


def get_scheduler(anylog_conn:anylog_connector.AnyLogConnector, schedule_number:int=None, destination:str=None,
               execute_cmd:bool=True, view_help:bool=False):
    """
    Check if a scheduler is active or not
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/alerts%20and%20monitoring.md#view-scheduled-commands
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog
        schedule_number:int - schedule number (ex `run schedule 1`
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - execute `help` against `set license`
    :params:
        status:bool
        headers:dict - REST header
    :return:
        if view_help is True - will print information regarding command and return None
        if scheduler_number is not None - will check if a scheduler process exists and return
            True if exists
            False if DNE
        else - return raw results of command
    """
    command = "get scheduler"
    if schedule_number is not None:
        command += " " + str(schedule_number)

    output = get_cmd(anylog_conn=anylog_conn, command=command, destination=destination, execute_cmd=execute_cmd,
                     view_help=view_help)

    if execute_cmd is False or view_help is True: # print command or view help
        return output
    elif execute_cmd is True and schedule_number is None: # print schedule
        return output
    elif "node declared" not in output and schedule_number is not None: # scheduled process is running
        return True
    else: # scheduled process(es) not running
        return False


def get_msg_client(anylog_conn:anylog_connector.AnyLogConnector, topic:str=None, broker:str=None, id:int=None,
                   destination: str = None, execute_cmd: bool = True, view_help:bool=False):
    """
    Check whether a msg client is active or not
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20calls.md#get-msg-clients
    :args:
        anylog_conn::anylog_connector.AnyLogConnector - connection to AnyLog via REST
        topic:str - topic to check for
        broker:str - IP:Port client is associated with
        id:int - client ID
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
       view_help:bool - get info regarding command
    :params:
        headers:dict - REST header information
        count:int - count number of conditions in `run msg client where`
    :return:
        results for command
    """
    command = "get msg client"

    if topic is not None or broker is not None or id is not None:
        count = 0
        command += " where"
        if topic is not None:
            command += f" topic={topic}"
            count += 1
        if broker is not None:
            if count >= 1:
                command += " and"
            command += f" broker={broker}"
            count += 1
        if id is not None:
            if count >= 1:
                command += " and"
            command += f" id={id}"

    return get_cmd(anylog_conn=anylog_conn, command=command, destination=destination, execute_cmd=execute_cmd,
                   view_help=view_help)