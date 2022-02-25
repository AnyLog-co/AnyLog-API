import json
from anylog_connection import AnyLogConnection
from support import print_error


def set_variables(anylog_conn:AnyLogConnection, key:str, value:str, exception:bool=False)->bool:
    """
    Add variable to AnyLog dictionary
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        key:str - variable name
        value:str - variable value
        exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    key = key.lstrip().rstrip()
    if isinstance(value, str):
        value = value.replace('"', '').replace("'", "").lstrip().rstrip()
        cmd = f'set {key}="{value}"'
    else:
        cmd = f'set {key}={value}'
    headers = {
        "command": cmd,
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r



def set_home_path(anylog_conn:AnyLogConnection, anylog_root_dir:str="!anylog_root_dir", exception:bool=False)->bool:
    """
    The following sets the home root path
    :command:
        set anylog home !anylog_root_dir
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        anylog_root_dir:str - AnyLog root dir path
        exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    headers ={
        'command': f'set anylog home {anylog_root_dir}',
        'User-Agent': 'AnyLog/1.23'
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def create_work_dirs(anylog_conn:AnyLogConnection, exception:bool=False)->bool:
    """
    create work directories for AnyLog
    :command:
        create work directories
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    headers = {
        "command": "create work directories",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def run_scheduler1(anylog_conn:AnyLogConnection, exception:bool=False)->bool:
    """
    Run base scheduler
    :command:
        run scheduler 1
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    headers = {
        "command": "run scheduler 1",
        "User-Agent": "AnyLog/1.23"
    }

    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def blockchain_sync_scheduler(anylog_conn:AnyLogConnection, source:str="master", time:str="!sync_time", dest:str="file",
                              connection:str="!master_node", exception:bool=False)->bool:
    """
    Set blockchain sync process
    :command:
        run blockchain sync where source=master and time=!sync_time and dest=file and connection=!master_node
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        source:str - blockchain source
        time:str - how often to sync blockchain
        dest:str - destination of copy of blockchain
        connection:str - REST connection info
        exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    headers = {
        "command": f"run blockchain sync where source={source} and time={time} and dest={dest} and connection={connection}",
        "User-Agent": "AnyLog/1.23"
    }

    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def schedule_task(anylog_conn:AnyLogConnection, time:str, name:str, task:str, exception:bool=False)->bool:
    """
    Execute Task
    :command:
        schedule time = 1 day and name = "Remove Old Partitions" task drop partition where dbms=!default_dbms and table =!table_name and keep=!partition_keep
    :args:
       anylog_conn:AnyLogConnection - connection to AnyLog
       time:str - how often to run the task
       name:str - task name
       task:str - The actual task to run
       exception:bool - whether to print exception
    :params:
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    headers = {
        "command": f"schedule time={time} and name={name} task {task}",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def exit_cmd(anylog_conn:AnyLogConnection, process:str=None, exception:bool=False)->bool:
    """
    Exit an AnyLog command - if no process is set will exit AnyLog completely
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        process:str - AnyLog process to exit
            exit tcp
            exit rest
            exit scripts
            exit scheduler
            exit synchronizer
            exit mqtt
            exit kafka
            exit smtp
            exit workers
        exception:bool - whether to print exception
    :params:
        cmd:str - command to execute
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        r
    """
    cmd = "exit"
    if process is not None:
        cmd += f" {process}"
    headers = {
        "command": cmd,
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def set_script(anylog_conn:AnyLogConnection, script_path:str, script_content:str, exception:bool=False)->bool:
    """
    Given a script_path set content into it
    :command:
        set script autoexec.json [script data]
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        script_path:str - file to write content to
        script_content:str - content to write to file
        exception:bool - whether to print exception
    :params:
        payload:str - content to write into file
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    """
    if isinstance(script_content, dict):
        payload = f"<script_content={json.dumps(script_content)}>"
    else:
        payload = f"<script_contnent={script_content}>"

    headers = {
        "command": f"set script {script_path} !script_content",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=payload)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r


def process_script(anylog_conn:AnyLogConnection, script_path:str, exception:bool=False)->bool:
    f"""
    Given a script_path set content into it
    :command:
        process {script_path}
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        script_path:str - script to execute
        exception:bool - whether to print exception
    :params: 
        header:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return: 
        r
    """
    headers = {
        "command": f"process {script_path}",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers, payload=None)
    if exception is True and r is False:
        print_error(error_type="POST", cmd=headers['command'], error=error)
    return r
