import json
import requests

__version__ = "beta"
__author__ = "Ori Shadmon"
__copyright__ = "Copyright (c) AnyLog, Co"

def get_location(exception:bool=False)->str:
    """
    Get location from  https://ipinfo.io/json
    :args:
        exception:bool - whether or not to print exception(s)
    :params:
        location:str - location from URL
        r:requests.models.Response- request response
    :return:
        location
    """
    location = '0.0, 0.0'
    try:
        r = requests.get(url='https://ipinfo.io/json')
    except Exception as e:
        if exception is True:
            print(f"Failed to execute GET against 'https://ipinfo.io/json' (Error {e})")
    else:
        try:
            location = r.json()['loc']
        except Exception as e:
            if exception is True:
                print(f'Failed to extract location (Error {e})')
    return location


def validate_dictionary(anylog_dict:dict={})->dict:
    """
    Validate if needed values exist in dictionary
    if something is miissing, fix it so code will work
    :args:
        anylog_dict:dict - dictionary to validate e
    :return:
        anylog_dict
    """
    # general
    if 'company_name' not in anylog_dict:
        anylog_dict['company_name'] = 'New Company'

    # database [default: sqlite]
    if 'db_type' not in anylog_dict:
        anylog_dict['db_type']='sqlite'
        anylog_dictionary['db_ip'] = None
        anylog_dictionary['db_port'] = None
        anylog_dictionary['db_user'] = None
        anylog_dictionary['db_passwd'] = None
    elif anylog_dict['db_type'] not in ['psql', 'sqlite']:
        anylog_dict['db_type'] = 'sqlite'
    elif anylog_dict['db_type'] == 'psql':
        if 'db_port' not in anylog_dict:
            anylog_dict['db_port'] = 5432
        if 'db_ip' not in anylog_dict or 'db_user' not in anylog_dict or 'db_passwd' not in anylog_dict:
            anylog_dict['db_type'] = 'sqlite'

    # blockchain sync [default: enabled]
    if 'enable_blockchain_sync' not in anylog_dict:
        anylog_dict['enable_blockchain_sync'] = 'true'
    if 'blockchain_source' not in anylog_dict:
        anylog_dict['blockchain_source'] = 'master'
    if 'sync_time' not in anylog_dict:
        anylog_dict['sync_time'] = '30 seconds'
    if 'blockchain_destination' not in anylog_dict:
        anylog_dict['blockchain_destination'] = 'file'
    if 'master_node' not in anylog_dict:
        anylog_dict['master_node'] = f"127.0.0.1:{anylog_dict['anylog_server_port']}"

    # partitioning
    if 'enable_partitions' in anylog_dict and anylog_dict['enable_partitions'] == 'true':
        if 'partition_table' not in anylog_dict:
            anylog_dict['partition_table'] = '*'
        if 'partition_column' not in anylog_dict:
            anylog_dict['partition_column'] = 'timestamp'
        if 'partition_interval' not in anylog_dict['partition_interval']:
            anylog_dict['partition_interval'] = '15 days'
        if 'partition_keep' not in anylog_dict['partition_keep']:
            anylog_dict['partition_keep'] = 6 # ~3 months
        if 'partition_sync' not in anylog_dict['partition_sync']:
            anylog_dict['partition_sync'] = '1 day'
    else:
        anylog_dict['enable_partitions'] = 'false'

    # MQTT
    if 'enable_mqtt' in anylog_dict and anylog_dict['enable_mqtt'] == 'true':
        if 'broker' not in anylog_dict or 'mqtt_port' not in anylog_dict:
            anylog_dict['enable_mqtt'] = 'false'

    # MQTT configs
    if anylog_dict['enable_mqtt'] == 'true':
        if 'mqtt_log' not in anylog_dict:
            anylog_dict['mqtt_log'] = 'false'
        elif anylog_dict['mqtt_log'] != 'false' and anylog_dict['mqtt_log'] != 'true':
            anylog_dict['mqtt_log'] = 'false'
        if 'mqtt_user' not in anylog_dict:
            anylog_dict['mqtt_user'] = ''
        if 'mqtt_passwd' not in anylog_dict:
            anylog_dict['mqtt_passwd'] = ''
        if 'topic_name' not in anylog_dict:
            anylog_dict['topic_name'] = '*'

    return anylog_dict


def print_error(error_type:str, cmd:str, error:str):
    """
    Print Error message
    :args:
        error_type:str - Error Type
        cmd:str - command that failed
        error:str - error message
    :print:
        error message
    """
    if isinstance(error, int):
        print(f'Failed to execute {error_type} for "{cmd}" (Network Error: {error})')
    else:
        print(f'Failed to execute {error_type} for "{cmd}" (Error: {e})')


def format_mqtt_cmd(broker:str, port:str, mqtt_user:str='', mqtt_passd:str='', mqtt_log:bool=False,
                      topic_name:str='*', topic_dbms:str='', topic_table:str='', columns:dict={})->str:
    """
    Given the params for an MQTT generate MQTT call
    :args:
        broker:str - broker connection information
        port:str - port correlated to broker
        mqtt_user:str - user for accessing MQTT
        mqtt_passswd:str - password correlated to user
        mqtt_log:bool - whether to print MQTT logs or not
        topic_name:str - MQTT topic
        topic_dbms:str - database
        topic_name:str - table
        columns:dict - columns to extract
            {
                "timestamp": {"value": "bring [ts]", "type": "timestamp"},
                "value": {"value": "bring [value]", "type": "float"}
            }
    :params:
        cmd:str - full MQTT call
        topic:str - topic component for MQTT call
    :return:
        cmd
    """
    cmd = f"run mqtt client where broker={broker} and port={port}"
    if mqtt_user != '' and mqtt_passd != '':
        cmd += f" and user={mqtt_user} and password={mqtt_passd}"
    if broker == 'rest':
        cmd += " and user-agent=anylog"
    cmd += " and log=false"
    if mqtt_log is True:
        cmd = cmd.replace('false', 'true')
    topic = f"name={topic_name}"
    if topic_dbms != '':
        topic += f' and dbms="{topic_dbms}"'
    if topic_table != '':
        topic += f' and table="{topic_table}"'
    if columns != {} :
        for column in columns:
            if columns[column]['type'] not in ['str', 'int', 'float', 'bool', 'timestamp']:
                columns[column]['type'] = 'str'
            if columns[column]['type'] == 'timestamp':
                topic += f' and column.{column}.timestamp="%s"' % columns[column]['value']
            else:
                topic += f' and column.{column}=(value="%s" and type=%s)' % (columns[column]['value'], columns[column]['type'])
    cmd += f" and topic=({topic})"
    return cmd


def read_file(file_name:str, exception:bool=False)->dict:
    """
    Read content in file
    :args:
        file_name:str - file to extract content from
    :params:
        file_content:dict - content in autoexec file
    :return:
        file content
    """
    file_content = {}
    try:
        with open(file_name, 'r') as rf:
            try:
                file_content = json.load(rf)
            except:
                try:
                    file_content = rf.read()
                except Exception as e:
                    if exception is True:
                        print(f"Failed to read content in {file_name} (Error: {e})")
    except Exception as e:
        if exception is True:
            print(f"Failed to open file {file_name} (Error: {e})")

    return file_content


class AnyLogConnection:
    """
    The following are the base support for AnyLog via REST
        - GET: extract information from AnyLog (information + queries)
        - POST: Execute or POST command against AnyLog
        - POST_POLICY: POST information to blockchain
    The code also contain classmethods for "generic" GET/PUT/POST commands
    """
    def __init__(self, conn:str, auth:tuple=None, timeout:int=30):
        """
        The following are the base support for AnyLog via REST
            - GET: extract information from AnyLog (information + queries)
            - POST: Execute or POST command against AnyLog
            - POST_POLICY: POST information to blockchain
        The code also contain classmethods for "generic" GET/PUT/POST commands
        :url:
            Using Rest: https://github.com/AnyLog-co/documentation/blob/master/using%20rest.md
        :param:
            conn:str - REST connection info
            auth:tuple - Authentication information
            timeout:int - REST timeout
        """
        self.conn = conn
        self.auth = auth
        self.timeout = timeout

    def get(self, headers:dict)->(equests.models.Response, str):
        """
        requests GET command
        :args:
            headers:dict - header to execute
        :param:
            r:requests.response - response from requests
            error:str - If exception during error
        :return:
            r, error
        """
        error = None

        try:
            r = requests.get('http://%s' % self.conn, headers=headers, auth=self.auth, timeout=self.timeout)
        except Exception as e:
            error = str(e)
            r = False

        return r, error

    @classmethod
    def get_help(cls, anylog_conn:AnyLogConnection, help_cmd:str=None, exception:bool=None)->str:
        """
        Execute the `help` command against AnyLog
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            help_cmd:str - specific command to get help for
            exception:bool - whether to print exception
        :params:
            output:str - content from help
            cmd:str - command to execute
            header:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            the results from help, else None
        """
        output = None
        cmd = "help"
        if help_cmd is not None:
            cmd += f" {help_cmd}"
        headers = {
            "command": cmd,
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.get(headers=headers)
        if exception is True and r is False:
            print_error(print_error='GET', cmd=headers['command'], error=error)
        else:
            try:
                output = r.text
            except Exception as e:
                if exception is True:
                    print(f"Failed to extract information for cmd: {cmd} (Error: {e})")
        return output

    @classmethod
    def validate_status(cls, anylog_conn:AnyLogConnection, exception:bool=False)->bool:
        """
        Validate if Node is running or not
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            exception:bool - whether to print exception
        :params:
            status:bool
            header:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            if success return True
            else False
        """
        status = False
        headers = {
            'command': 'get status',
            'User-Agent': 'AnyLog/1.23'
        }
        r, error = anylog_conn.get(headers=headers)
        if exception is True and r is False:
            print_error(print_error='GET', cmd=headers['command'], error=error)
        elif 'running' in r.text and 'not' not in r.text:
            status = True
        return status

    @classmethod
    def get_dictionary(cls, anylog_conn:AnyLogConnection, exception:bool=False)->dict:
        """
        Get dictionary in dictionary format
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            exception:bool - whether to print exception
        :params:
            dictionary:dict - dictionary of values extracted from AnyLog
            header:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            dictionary as dict
        """
        dictionary = {}
        headers = {
            "command": "get dictionary where format=json",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.get(headers=headers)
        if exception is True and r is False:
            print_error(print_error='GET', cmd=headers['command'], error=error)
        else:
            try:
                dictionary = r.json()
            except Exception as e:
                try:
                    dictionary = r.text
                except Exception as e:
                    if exception is True:
                        print(f"Failed to extract content for {headers['command']} (Error: {e})")
        return dictionary

    @classmethod
    def get_event_log(cls, anylog_conn:AnyLogConnection, exception:bool=False)->dict:
        """
        Get event log in dictionary format
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            exception:bool - whether to print exception
        :params:
            event_log:dict - event log extracted from AnyLog
            header:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            dictionary as dict
        """
        event_log = {}
        headers = {
            "command": "get event log where format=json",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.get(headers=headers)
        if exception is True and r is False:
            print_error(print_error='GET', cmd=headers['command'], error=error)
        else:
            try:
                event_log = r.json()
            except Exception as e:
                try:
                    event_log = r.text
                except Exception as e:
                    if exception is True:
                        print(f"Failed to extract content for {headers['command']} (Error: {e})")
        return event_log

    @classmethod
    def get_error_log(cls, anylog_conn:AnyLogConnection, exception:bool=False)->dict:
        """
        Get error log in dictionary format
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            exception:bool - whether to print exception
        :params:
            error_log:dict - error log extracted from AnyLog
            header:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            dictionary as dict
        """
        error_log = {}
        headers = {
            "command": "get error log where format=json",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.get(headers=headers)
        if exception is True and r is False:
            print_error(print_error='GET', cmd=headers['command'], error=error)
        else:
            try:
                error_log = r.json()
            except Exception as e:
                try:
                    error_log = r.text
                except Exception as e:
                    if exception is True:
                        print(f"Failed to extract content for {headers['command']} (Error: {e})")
        return error_log

    @classmethon
    def get_processes(cls, anylog_conn:AnyLogConnection, exception:bool=False)->dict:
        """
        Get processes in dictionary format
        :command:
            get processes where format=json
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            exception:bool - whether to print exception
        :params:
            get_process:dict - get processes as a dictionary
            header:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            dictionary as dict
        """
        get_process = {}
        headers = {
            "command": "get processes where format=json",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.get(headers=headers)
        if exception is True and r is False:
            print_error(print_error='GET', cmd=headers['command'], error=error)
        else:
            try:
                get_process = r.json()
            except Exception as e:
                try:
                    get_process = r.text
                except Exception as e:
                    if exception is True:
                        print(f"Failed to extract content for {headers['command']} (Error: {e})")
        return get_process

    @classmethod
    def get_hostname(cls, anylog_conn:AnyLogConnection, exception:bool=False)->str:
        """
        Extract hostname
        :command:
            get hostname
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            exception:bool - whether to print exception
        :params:
            hostname:str - hostname
            header:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            hostname
        """
        hostname = ''
        headers = {
            "command": "get hostname",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.get(headers=headers)
        if exception is True and r is False:
            print_error(print_error='GET', cmd=headers['command'], error=error)
        else:
            try:
                hostname = r.text
            except Exception as e:
                if exception is True:
                    print(f'Failed to extract hostname (Error: {e})')

        return hostname

    def post(self, headers:dict, payload:dict=None)->(equests.models.Response, str):
        """
        Execute POST command against AnyLog. payload is required under the following conditions:
            1. payload can be data that you want to add into AnyLog, in which case you should also have an
                MQTT client of type REST running on said node
            2. payload can be a policy you'd like to add into the blockchain
            3. payload can be a policy you'd like to remove from the blockchain
                note only works with Master, cannot remove a policy on a real blockchain like Ethereum.
        :args:
            headers:dict - request headers
            payloads:dict - data to post
        :params:
            r:requests.response - response from requests
            error:str - If exception during error
        :return:
            r, error
        """
        error = None
        try:
            r = requests.post('http://%s' % self.conn, headers=headers, data=payload, auth=self.auth,
                              timeout=self.timeout)
        except Exception as e:
            error = str(e)
            r = False
        else:
            if int(r.status_code) != 200:
                error = str(r.status_code)
                r = False
        return r, error

    @classmethod
    def set_variables(cls, anylog_conn:AnyLogConnection, key:str, value:str, exception:bool=False)->bool:
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

    @classmethod
    def set_home_path(cls, anylog_conn:AnyLogConnection, anylog_root_dir:str="!anylog_path",
                      exception:bool=False)->bool:
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
        headers = {
            'command': f'set anylog home {anylog_root_dir}',
            'User-Agent': 'AnyLog/1.23'
        }
        r, error = anylog_conn.post(headers=headers, payload=None)
        if exception is True and r is False:
            print_error(error_type="POST", cmd=headers['command'], error=error)
        return r

    @classmethod
    def create_work_dirs(cls, anylog_conn:AnyLogConnection, exception:bool=False)->bool:
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

    @classmethod
    def run_scheduler1(cls, anylog_conn:AnyLogConnection, exception:bool=False)->bool:
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

    @classmethod
    def schedule_task(cls, anylog_conn:AnyLogConnection, time:str, name:str, task:str, exception:bool=False)->bool:
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

    @classmethod
    def exit_cmd(cls, anylog_conn:AnyLogConnection, process:str=None, exception:bool=False)->bool:
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

    @classmethod
    def set_script(cls, anylog_conn:AnyLogConnection, script_path:str, script_content:str, exception:bool=False)->bool:
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

    @classmethod
    def process_script(cls, anylog_conn:AnyLogConnection, script_path:str, exception:bool=False)->bool:
        """
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

    def put(self, headers:dict, payload:str)->(equests.models.Response, str):
        """
        Execute a PUT command against AnyLog - mainly used for Data
        :args:
            headers:dict - header to execute
        :param:
            r:requests.response - response from requests
            error:str - If exception during error
        :return:
            r, error
        """
        error = None
        try:
            r = requests.put('http://%s' % self.conn, auth=self.auth, timeout=self.timeout, headers=headers,
                             data=payload)
        except Exception as e:
            error = str(e)
            r = False
        else:
            if int(r.status_code) != 200:
                error = str(r.status_code)
                r = False

        return r, error


class DeploymentCalls:
    """
    Functions related specifically to deploying either Publisher, Operator or MQTT processs
    """
    @classmethod
    def run_mqtt_client(cls, anylog_conn:AnyLogConnection, broker:str, port:str, mqtt_user:str='', mqtt_passd:str='',
                        mqtt_log:bool=False, topic_name:str='*', topic_dbms:str='', topic_table:str='',
                        columns:dict={}, exception:bool=False)->bool:
        """
        Run MQTT client
        :url:
            https://github.com/AnyLog-co/documentation/blob/master/message%20broker.md#subscribing-to-a-third-party-broker
        :command:
            run mqtt client where \
                broker={broker} and \
                port={port} and \
                [user-agent=anylog] and \
                [user={mqtt_user} and] \
                [password={mqtt_password} and] \
                log={mqtt_log} and \
                topic=( \
                    name={mqtt_topic_name} and
                    dbms={mqtt_topic_dbms} and
                    table={mqtt_topic_table} and \
                    column.timestamp.timestamp={mqtt_column_timestamp} and \
                    column.value=( \
                        value={mqtt_column_value} and \
                        type={mqtt_column_value_type} \
                    ) \
                )
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            broker:str - broker connection information
            port:str - port correlated to broker
            mqtt_user:str - user for accessing MQTT
            mqtt_passswd:str - password correlated to user
            mqtt_log:bool - whether to print MQTT logs or not
            topic_name:str - MQTT topic
            topic_dbms:str - database
            topic_name:str - table
            columns:dict - columns to extract
                {
                    "timestamp": {"value": "bring [ts]", "type": "timestamp"},
                    "value": {"value": "bring [value]", "type": "float"}
                }
            exception:bool - whether to print exception
        :params:
            cmd:str - MQTT command to execute
            header:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            r
        """
        cmd = format_mqtt_cmd(broker=broker, port=port, mqtt_user=mqtt_user, mqtt_passd=mqtt_passd, mqtt_log=mqtt_log,
                              topic_name=topic_name, topic_dbms=topic_dbms, topic_table=topic_table, columns=columns)
        headers = {
            "command": cmd,
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.post(headers=headers, payload=None)
        if exception is True and r is False:
            print_error(error_type="POST", cmd=headers['command'], error=error)
        return r

    @classmethod
    def set_threshold(cls, anylog_conn:AnyLogConnection, write_immediate:bool=True, exception:bool=False)->bool:
        """
        Set buffer threshold
        :command:
            set buffer threshold where write_immediate = true
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            write_immediate:bool - whether to set threshold to immediate
            exception:bool - whether to print exception
        :params:
            cmd:str - command to execute
            header:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            r
        """
        cmd = "set buffer threshold"
        if write_immediate is True:
            cmd += " where write_immediate=true"
        headers = {
            "command": cmd,
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.post(headers=headers, payload=None)
        if exception is True and r is False:
            print_error(error_type="POST", cmd=headers['command'], error=error)
        return r

    @classmethod
    def run_streamer(cls, anylog_conn:AnyLogConnection, exception:bool=False)->bool:
        """
        Set streamer
        :command:
            run streamer
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
            "command": "run streamer",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.post(headers=headers, payload=None)
        if exception is True and r is False:
            print_error(error_type="POST", cmd=headers['command'], error=error)
        return r

    @classmethod
    def run_operator(cls, anylog_conn:AnyLogConnection, create_table:bool=True, update_tsd_info:bool=True, archive:bool=True,
                     distributor:bool=True, master_node:str="!master_node", exception:bool=False)->bool:
        """
        Start Operator process
        :command:
            run operator where create_table=true and update_tsd_info=true and archive=true and distributor=true and master_node={master_node}
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            create_table:bool - Whether to create/declare table if DNE
            update_tsd_info:str - Whether to update tsd_info table
            archive:str - whether to archive (or backup) files
            distributor:str - whether to distribute data among other operators in the cluster
             master_node:str - which master to work against
            exception:bool - whether to print exception
        :params:
            cmd:str - command to execute
            header:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            r
        """
        cmd = f"run operator where create_table=true and update_tsd_info=true and archive=true and distributor=true and master_node={master_node}"
        if create_table is False:
            cmd = cmd.replace("create_table=true", "create_table=false")
        if update_tsd_info is False:
            cmd = cmd.replace("update_tsd_info=true", "update_tsd_info=false")
        if archive is False:
            cmd = cmd.replace("archive=true", "archive=false")
        if distributor is False:
            cmd = cmd.replace("distributor=true", "distributor=false")

        headers = {
            "command": cmd,
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.post(headers=headers, payload=None)
        if exception is True and r is False:
            print_error(error_type="POST", cmd=headers['command'], error=error)
        return r


class DatabaseCalls:
    """
    The following methods are used to to execute database related commands
        --> list connected database(s)
        --> disconnect/connect to database
        --> cheeck if table exists
        --> create tablee
        --> set & check partitions
    """
    @classmethod
    def get_dbms(cls, anylog_conn:AnyLogConnection, exception:bool=False)->list:
        """
        Get list of database connected locally
        :command:
            get databases
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            exception:bool - whether to print exception
        :params:
            db_list:list - list of databases
            headers:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            db_list
        """
        db_list = []
        headers = {
            "command": "get databases",
            "User-Agent": "AnyLog/1.23"
        }

        r, error = anylog_conn.get(headers=headers)
        if exception is True and r is False:
            print_error(error_type="GET", cmd=headers['command'], error=error)
        else:
            try:
                output = r.text
            except Exception as e:
                if exception is True:
                    print(f"Failed to extract result for {headers['command']} (Exception: {e})")
            else:
                if output != 'No DBMS connections found':
                    for row in output.split('\n'):
                        if 'sqlite' in row or 'psql' in row:
                            db_list.append(row.split(' ')[0].rstrip().lstrip())
        return db_list

    @classmethod
    def connect_dbms(cls, anylog_conn:AnyLogConnection, db_name:str, db_type:str="sqlite", db_ip:str="127.0.0.1",
                     db_port:int=5432, db_user:str="", db_passwd:str="", exception:bool=False)->bool:
        """
        Connect to logical database
        :command:
            connect dbms {db_name} where type={db_type} and user={db_user} and password={db_passwd} and ip={db_ip} and port={db_port}
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            db_name:str - logical database name
            db_type:str - logical database type (ex SQLite or PSQL)
            db_ip:str - database IP address
            db_port:str - database port
            db_user:str - database user
            db_passwd:str - password correlated to database user
            exception:bool - whether to print exception
        :params:
            header:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            r
        """
        cmd = f"connect dbms {db_name} where type={db_type}"
        if db_type != 'sqlite':
            cmd += f" and ip={db_ip} and port={db_port} and user={db_user} and password={db_passwd}"
        headers = {
            'command': cmd,
            'User-Agent': 'AnyLog/1.23'
        }
        r, error = anylog_conn.post(headers=headers, payload=None)
        if exception is True and r is False:
            print_error(error_type="POST", cmd=headers['command'], error=error)
        return r

    @classmethod
    def disconnect_dbms(cls, anylog_conn:AnyLogConnection, db_name:str, exception:bool=False)->bool:
        """
        Disconnect database
        :command:
            disconnect dbms {db_name}
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            db_name:str - logical database name
            exception:bool - whether to print exception
        :params:
            headers:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            r
        """
        headers = {
            "command": f"disconnect dbms {db_name}",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.post(headers=headers, payload=None)
        if exception is True and r is False:
            print_error(error_type="POST", cmd=headers['command'], error=error)
        return r

    @classmethod
    def check_table(cls, anylog_conn:AnyLogConnection, db_name:str, table_name:str, exception:bool=False)->bool:
        """
        Validate if table if exists
        :command:
            get table local status where dbms={db_name} and name={table_name}
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            db_name:str - logical database name
            table_name:str - table to check if exists
            exception:bool - whether to print exception
        :params:
            status:bool
            headers:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            if table exists return True, else False
        """
        status = False
        headers = {
            "command": f"get table local status where dbms={db_name} and name={table_name}",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.get(headers=headers)
        if exception is True and r is False:
            print_error(error_type="GET", cmd=headers['command'], error=error)
        else:
            try:
                if r.json()['local'] == 'true':
                    status = True
            except:
                if 'true' in r.text:
                    status = True
        return status

    @classmethod
    def create_table(cls, anylog_conn:AnyLogConnection, db_name:str, table_name:str, exception:bool=False)->bool:
        """
        Create table based on params
        :command: 
            create table {table_name} where dbms={db_name}
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            db_name:str - logical database name
            table_name:str - table to create
            exception:bool - whether to print exception
        :params:
            headers:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            r
        """
        headers = {
            "command": f"create table {table_name} where dbms={db_name}",
            "User-Agent": "AnyLog/1.23"
        }

        r, error = anylog_conn.post(headers=headers, payload=None)
        if exception is True and r is False:
            print_error(error_type="POST", cmd=headers['command'], error=error)
        return r

    @classmethod
    def set_partitions(cls, anylog_conn:AnyLogConnection, db_name:str, table:str="*",
                       partition_column:str="timestamp", partition_interval:str="15 days",
                       exception:bool=False) -> bool:
        """
        Set partitions
        :command:
            partition !default_dbms * using !partition_column by !partition_interval
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            db_name:str - logical database to partition
            table:str - table to partition against, if set to '*' partition all tables in database
            partition_column:str - column to partition by
            partition_interval:str - partition interval
            exception:bool - whether to print exception
        :params:
            header:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            r
        """
        headers = {
            "command": f"partition {db_name} {table} using {partition_column} by {partition_interval}",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.post(headers=headers, payload=None)
        if exception is True and r is False:
            print_error(error_type="POST", cmd=headers['command'], error=error)
        return r

    @classmethod
    def check_partitions(cls, anylog_conn:AnyLogConnection, exception:bool=False) -> bool:
        """
        Check whether partitions already exist or not
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            exception:bool - whether to print exception
        :params:
            status:bool
            header:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            status - if partition DNE return False, else return True
        """
        status = False
        headers = {
            "command": "get partitions",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.get(headers=headers)
        if exception is True and r is False:
            print_error(error_type="POST", cmd=headers['command'], error=error)
        elif int(r.status_code) == 200:
            try:
                if r.text != 'No partitions declared':
                    status = True
            except Exception as e:
                if exception is True:
                    print(f'Failed to check whether partitions are set or not (Error {e})')
        return status


class BlockchainCalls:
    """
    The following is intended  to provide support for using the AnyLog blockchain
    :function:
        --> GET
        --> CREATE policy
        --> DROP policy
        --> blockchain sync
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/blockchain%20commands.md
    """
    @classmethod
    def blockchain_get(cls, anylog_conn:str, policy_type:str='*', where_condition:str=None, bring_param:str=None,
                       bring_condition:str=None, separator:str=None, exception:bool=False)->dict:
        """
        Execute blockchain get based on params
        :command:
            blockchain get operator where company=AnyLog  bring [operator][name] separator=,
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            policy_type:str - policy type to get from blockchain
            where_condition:str - where conditions
            bring_param:str - param correlated to bring command (ex. first)
            bring_condition:str - bring conditions
            separator:str - character to separate results by
        :params:
            blockchain_data:dict - Results from blockchain
            cmd:str - command to execute
            headers:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            blockchain_data
        """
        blockchain_data = None

        cmd = f"blockchain get {policy_type}"
        if where_condition is not None:
            cmd += f" where {where_condition}"
        if bring_condition is not None and bring_param is not None:
            cmd += f" bring.{bring_param} {bring_condition}"
        elif bring_condition is not None:
            cmd += f" bring {bring_condition}"
        if separator is not None:
            cmd += f" separator={separator}"

        headers = {
            "command": cmd,
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.get(headers=headers)
        if exception is True and r is False:
            print_error(error_type="GET", cmd=headers['command'], error=error)
        else:
            try:
                blockchain_data = r.json()
            except Exception as e:
                try:
                    blockchain_data = r.text
                except Exception as e:
                    if exception is True:
                        print(f"Failed to extract results for {cmd} (Error: {e})")
        return blockchain_data

    @classmethod
    def declare_policy(cls, anylog_conn:AnyLogConnection, policy_type:str, company_name:str, policy_values:dict={},
                       master_node:str="!master_node", exception:bool=False)->bool:
        """
        Process to create policy in (blockchain) ledger
        :steps:
            1. prepare policy - Adds an ID and a date attributes to an existing policy.
            2. insert policy - Add a new policy to the ledger in one or more blockchain platform.s
        :commands:
            blockchain prepare policy !new_policy
            blockchain insert where policy=!new_policy and local=true and master=!master_node
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            policy_type:str - policy type (ex. master, operator, cluster)
            company_name:str - name of company policy is correlated to
            policy_values:dict - values correlated to policy type
            master_node:str - master node to send policy to
            exception:bool - whether the command failed & why
        :params:
            status:bool
            policy:dict - policy to post on blockchain
            payload:str - policy converted to string
            headers:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            status
        """
        status = True
        if not isinstance(policy_values, dict):
            try:
                policy_values = json.loads(policy_values)
            except:
                pass
        if isinstance(policy_values, dict) and  'company' not in policy_values:
            policy_values['company'] = company_name

        policy = {policy_type: policy_values}

        try: # convert policy to AnyLog JSON policy object
            payload = f"<new_policy={json.dumps(policy)}>"
        except Exception as e:
            status = False
            if exception is True:
                print(f"Failed to convert {policy} to string (Error: {e})")

        if status is True: # prepare policy
            headers = {
                "command": "blockchain prepare policy !new_policy",
                "User-Agent": "AnyLog/1.23"
            }
            r, error = anylog_conn.post(headers=headers, payload=payload)
            if r is False:
                status = False
                if exception is True:
                    print_error(error_type="POST", cmd=headers['command'], error=error)

        if status is True: # insert policy
            headers = {
                "command": f"blockchain insert where policy=!new_policy and local=true and master={master_node}",
                "User-Agent": "AnyLog/1.23"
            }
            r, error = anylog_conn.post(headers=headers, payload=payload)
            if r is False:
                status = False
                if exception is True:
                    print_error(error_type="POST", cmd=headers['command'], error=error)

        return status

    @classmethod
    def drop_policy(cls, anylog_conn:AnyLogConnection, policy:dict={}, exception:bool=False)->bool:
        """
        Given a policy execute the drop command
        :command:
            blockchain drop policy !policy
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            policy:dict - policy command
            exception:bool - whether the command failed & why
        :params:
            status:bool
            policy_str:str - policy as a string
            headers:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            status
        """
        status = True
        if isinstance(policy, dict):
            policy_str = json.dumps(policy)
        else:
            policy_str = policy
        payload = f"<drop_policy={policy_str}>"
        headers = {
            "command": "blockchain drop policy !drop_policy",
            "User-Agent": "AnyLog/1.23"
        }

        r, error = anylog_conn.post(headers=headers, payload=payload)
        if r is False:
            status = False
            if exception is True:
                print_error(error_type="POST", cmd=headers['command'], error=error)
        return status

    @classmethod
    def set_blockchain_sync(cls, anylog_conn:AnyLogConnection, source:str="master", time:str="30 seconds",
                            dest:str="file", connection:str="!master_node", exception:bool=False)->bool:
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

    @classmeethod
    def blockchain_sync(cls, anylog_conn:AnyLogConnection, exception:bool=False)->bool:
        """
        Execute run blockchain sync
        :command:
            run blockchain sync
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
            "command": "run blockchain sync",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.post(headers=headers, payload=None)
        if exception is True and r is False:
            print_error(error_type="POST", cmd=headers['command'], error=error)
        return r


class AuthenticationConfig:
    """
    The following is intended to provide support with configuring of authentication via REST
        --> Disable/enable authentication
        --> create public key
        --> get nodee
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/authentication.md
    """
    @classmethod
    def disable_authentication(cls, anylog_conn:AnyLogConnection, exception:bool=False)->bool:
        """
        disable authentication
        :params:
            set authentication off
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            exception:bool - whether to print exception
        :params:
            headers:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            r
        """
        headers = {
            "command": "set authentication off",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.post(headers=headers, payload=None)
        if exception is True and r is False:
            print_error(error_type="POST", cmd=headers['command'], error=error)
        return r

    @classmeethod
    def get_node_id(anylog_conn:AnyLogConnection, exception:bool=False)->str:
        """
        disable authentication
        :params:
            get node id
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            exception:bool - whether to print exception
        :params:
            output:str - placeholder containing Node ID extracted via REST
            headers:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            r
        """
        output = None
        headers = {
            "command": "get node id",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.get(headers=headers)
        if exception is True and r is False:
            print_error(error_type="GET", cmd=headers['command'], error=error)
        elif int(r.status_code) == 200:
            try:
                output = r.text
            except Exception as e:
                r = False
                if exception is Ture:
                    print(f"Failed to extract NODE ID (Error: {e})")
            else:
                r = output
        return r

    @classmethod
    def create_public_key(anylog_conn:AnyLogConnection, password='passwd', exception:bool=False)->bool:
        """
        Create a public key (will be located in AnyLog-Network/anylog/node_id.pem
        :command:
            id create keys for node where password = {password}
        :args:
            anylog_conn:AnyLogConnection - connection to AnyLog
            password:str - authentication password for key
            exception:bool - whether to print exception
        :params:
            headers:dict - REST header
            r:bool, error:str - whether the command failed & why
        :return:
            r
        """
        headers = {
            "command": f"id create keys for node where password={password}",
            "User-Agent": "AnyLog/1.23"
        }
        r, error = anylog_conn.post(headers=headers, payload=None)
        if exception is True and r is False:
            print_error(error_type="POST", cmd=headers['command'], error=error)
        return r








