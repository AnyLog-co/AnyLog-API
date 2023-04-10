from anylog_connector import AnyLogConnector
import generic_get_calls
import rest_support


def activate_license_key(anylog_conn:AnyLogConnector, license_key:str, exception:bool=False):
    """
    Enable license key
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        license_key:str - license key
        exception:bool - whether to print exceptions
    :params:
        status:bool - initially used as a list of True/False, but ultimately becomes True/False based on which has more
        headers:dict - REST header information
    :return:
        status
    """
    status = True
    headers = {
        "command": f"set license where activation_key = {license_key}",
        "User-Agent": "AnyLog/1.23"
    }

    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True:
            rest_support.print_rest_error(call_type='POST', cmd="set liicense key", exception=exception)

    return status


def add_dict_params(anylog_conn:AnyLogConnector, content:dict, exception:bool=False):
    """
    Add parameters to dictionary
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        content:dict - key/value pairs to add to dic
        exception:bool - whether to print exceptions
    :params:
        status:bool - initially used as a list of True/False, but ultimately becomes True/False based on which has more
        headers:dict - REST header information
    :return:
        if (at least 1) fails to POST then returns False, else True
    """
    status = []
    headers = {
        'command':  None,
        'User-Agent': 'AnyLog/1.23'
    }

    for key in content:
        headers['command'] = f'set {key} = {content[key]}'
        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status.append(False)
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], exception=exception)
        elif not isinstance(r, bool):
            status.append(True)

    num_false = status.count(False)
    num_true = status.count(True)

    status = True
    if False in status:
        status = False

    return status


def network_connect(anylog_conn:AnyLogConnector, conn_type:str, internal_ip:str, internal_port:int,
                    external_ip:str=None, external_port:int=None, bind:bool=True, threads:int=3, rest_timeout:int=30,
                    view_help:bool=False, exception:bool=False):
    """
    Connect to a network
    :args: 
        anylog_conn:AnyLogConnector - connecton to AnyLog 
        conn_type:str - connection type (TCP, REST, broker)
        internal_ip:str - internal/local  ip
        internal_port  - internal/local ip
        external_ip:str - external ip
        external_port:str - external port
        bind:bool - whether to bind or not
        threads:int - number of threads 
        rest_timeout:bool - REST timeout 
        view_help:bool - whether to print help information
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - print help information
    """
    # validate
    status = False
    if conn_type.upper() == 'TCP' or conn_type.upper() == 'REST' or conn_type.lower() == 'broker':
        status = None
    else:
        if exception is True:
            print(f'Invalid connection type: {conn_type}. Cannot execute connection')
        return status

    headers = {
        'command': rest_support.generate_connection_command(conn_type=conn_type, internal_ip=internal_ip,
                                                       internal_port=internal_port, external_ip=external_ip,
                                                       external_port=external_port, bind=bind, threads=threads,
                                                       rest_timeout=rest_timeout),
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def run_scheduler_1(anylog_conn:AnyLogConnector, view_help:bool=False, exception:bool=False):
    """
    Execute `run scheduler 1` command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/alerts%20and%20monitoring.md#invoking-a-scheduler
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog Node
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
    :return:
        True - success
        False - fails
        None - execute `help` command
    """
    status = None
    headers = {
        'command': 'run scheduler 1',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def declare_schedule_process(anylog_conn:AnyLogConnector, time:str, task:str, start:str=None, name:str=None,
                             view_help:bool=False, exception:bool=False):
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
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - print help
    :note:
        for schedule to start user needs to invoke it
    """
    status = None
    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command='schedule', exception=exception)
    else:
        command = f'schedule time={time}'
        if name is not None:
            command += f' and name="{name}"'
        if start is not None:
            command += f' and start="{start}"'
        command += f' task {task}'

        headers = {
            'command': command,
            'User-Agent': 'AnyLog/1.23'
        }

        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def run_scheduler(anylog_conn:AnyLogConnector, schedule_number:int=None, view_help:bool=False,
                  exception:bool=False):
    """
    invoke a scheduled process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/alerts%20and%20monitoring.md#invoking-a-scheduler
    :args:
        anylog_conn:AnyLogConnector - AnyLog REST connection information
        schedule_number:int - schedule number (ex `run schedule 1`
        view_help:bool - whether to print help informaton
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - print help
    """
    status=None
    headers = {
        'command': 'run scheduler',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        if schedule_number is not None:
            headers['command'] += f' {schedule_number}'

        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def set_buffer_threshold(anylog_conn:AnyLogConnector, db_name:str=None, table_name:str=None, time:str='60 seconds',
                         volume:str='10KB', write_immediate:bool=False, view_help:bool=False,
                         exception:bool=False):
    """
    Setting the buffer threshold
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#setting-and-retrieving-thresholds-for-a-streaming-mode
    :args:
        anylog_conn:AnyLogConnector - conneection to AnyLog via REST
        db_name:str - logical database name
        table_name:str - table name
        time:str - The time threshold to flush the streaming data
        volume:str - The accumulated data volume that calls the data flush process
        write_immediate:bool - Local database is immediate (independent of the calls to flush)
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - view help
    """
    status = None
    headers = {
        'command': 'set buffer threshold ',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        where_conditions = f"where time={time} and volume={volume}"

        if db_name is not None and table_name is not None:
            where_conditions = where_conditions.replace('where', f'where dbms={db_name} and table={table_name} and')
        elif db_name is not None and table_name is None:
            where_conditions = where_conditions.replace('where', f'where dbms={db_name} and')
        elif db_name is None and table_name is not None:
            where_conditions = where_conditions.replace('where', f'where table={table_name} and')
        if write_immediate is True:
            where_conditions += ' and write_immediate=true'
        else:
            where_conditions += ' and write_immediate=false'

        headers['command'] += where_conditions
        r, error = anylog_conn.post(headers=headers, payload=None)
        if r is False or int(r.status_code) != 200:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def enable_streamer(anylog_conn:AnyLogConnector, view_help:bool=False, exception:bool=False):
    """
    run streamer
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#streamer-process
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog Node
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - print help information
    """
    status = None
    headers = {
        'command': 'run streamer',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        r, error = anylog_conn.post(headers=headers)
        if r is False:
            rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def run_publisher(anylog_conn:AnyLogConnector, db_name:str='file_name[0]', table_name:str='file_name[1]',
                  watch_dir:str=None, bkup_dir:str=None, error_dir:dict=None, delete_json:bool=False,
                  delete_sql:bool=True, compress_json:bool=True, compress_sql:bool=False,
                  ledger_conn:str=None, view_help:bool=False, exception:bool=False):
    """
    Initiate `run publisher`
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#publisher-process
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        db_name:str - the segment in the file name from which the database name is taken
        table_name:str - the segment in the file name from which the table name is taken
        watch_dir:str - The directory monitored by the Publisher. Files placed on the Watch directory are processed by the Publisher.
        bkup_dir:str -  The directory location to store JSON and SQL files that were processed successfully.
        error_dir:str - The directory location to store files containing data that failed processing.
        delete_json:bool - True/False for deletion of the JSON file if processing is successful.
        delete_sql:bool - True/False for deletion of the SQL file if processing is successful.
        compress_json:bool - True/False to enable/disable compression of the JSON file.
        compress_sql:bool - True/False to enable/disable compression of the SQL file.
        ledger_conn:str - The IP and Port of a Master Node (if a master node is used).
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - print help information
    """
    status = None
    headers = {
        'command': f'run publisher where dbms_name={db_name} and table_name={table_name}',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        if watch_dir is not None:
            headers['command'] += f' and watch_dir={watch_dir}'
        if bkup_dir is not None:
            headers['command'] += f' and bkup_dir={bkup_dir}'
        if error_dir is not None:
            headers['command'] += f' and watch_dir={error_dir}'
        if delete_json is True:
            headers['command'] += f' and delete_json=true'
        else:
            headers['command'] += f' and delete_json=false'
        if compress_json is True:
            headers['command'] += f' and compress_json=true'
        else:
            headers['command'] += f' and compress_json=false'
        if delete_sql is True:
            headers['command'] += f' and delete_sql=true'
        else:
            headers['command'] += f' and delete_sql=false'
        if compress_sql is True:
            headers['command'] += f' and compress_sql=true'
        else:
            headers['command'] += f' and compress_sql=false'
        if ledger_conn is not None:
            headers['command'] += f' and master_node={ledger_conn}'

        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def run_operator(anylog_conn:AnyLogConnector, operator_id:str, create_table:bool=True, update_tsd_info:bool=True,
                 archive:bool=True, compress_json:bool=True, compress_sql:bool=True, threads:int=3,
                 ledger_conn: str = None, view_help:bool=False, exception:bool=False):
    """
    Run operator process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#operator-process
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        operator_id:str - (policy) ID of the operator policy
        craete_table:bool - A True value creates a table if the table doesn't exists.
        update_tsd_info - True/False to update a summary table (tsd_info table in almgm dbms) with status of files ingested.
        compress_json - True/False to enable/disable compression of the JSON file.
        compress_sql - True/False to enable/disable compression of the SQL file.
        archvive:bool - True/False to move JSON files to archive.
        threads:int - number of operator threads
        ledger_conn - The IP and Port of a Master Node (if a master node is used)
        view_help:bool - whether to print info about command
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - print help information
    """
    status = None
    headers = {
        'command': f'run operator where policy={operator_id} and create_table={create_table} and update_tsd_info={update_tsd_info} and archive={archive} and compress_json={compress_json} and compress_sql={compress_sql} and threads={threads}',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        if ledger_conn is not None:
            headers['command'] += f' and master_node={ledger_conn}'

        r, error = anylog_conn.post(headers=headers)
        if r is False:
            rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def execute_process(anylog_conn:AnyLogConnector, file_path:str, view_help:bool=False, exception:bool=False):
    """
    Execute an AnyLog file via REST - file must be accessible on the AnyLog instance
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/node%20configuration.md#the-configuration-process
    :args:
        anylog_conn:AnyLogConnector - AnyLog connection information
        file_path:str - file (on the AnyLog instance) to be executed
        view_help:bool - whether to print help
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:bool, error:str - whether the command failed & why
    :return:
        True - Success
        False - Fails
        None - print help information
    """
    status = None
    headers = {
        'command': 'process',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status