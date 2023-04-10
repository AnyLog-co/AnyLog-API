from anylog_connector import AnyLogConnector
import generic_get_calls
import generic_data_support
import rest_support
import support


def get_partitions(anylog_conn:AnyLogConnector, view_help:bool=False, exception:bool=False):
    """
    Check whether partitions exist
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#get-command
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog va RESt
        view_help:bool - whether to print help meessage
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        True -  if partitions are set
        None - if print help
        False - if no partitions
    """
    status = None
    headers = {
        'command': 'get partitions',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = False
        r, error = anylog_conn.get(headers=headers)
        if r is False and exception is True:
            rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            output = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)
            if output != 'No partitions declared':
                status = True

    return status


def get_msg_client(anylog_conn:AnyLogConnector, message_client_id:int=None, topic_name:str=None, broker:str=None,
                   view_help:bool=False, exception:bool=False):
    """
    View data coming in for message client
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20calls.md#get-msg-clients
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node via REST
        message_client_id:int - specific message client to view
        topic_name:str - MQTT topic name
        broker:str - MQTT broker:port
        view_help:bool - whether to print help or not
        exception:bool - whether to print exception
    :params:
        output:str - `get msg client results`
        headers:dict - REST header information
        r:requests.get, error:str - results from REST GET request
    :return:
        if view_hep is True - None
        else - output from command
    """
    output = None
    headers = {
        'command': 'get msg client',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        if message_client_id is not None or topic_name is not None or broker is not None or port is not None:
            where_conditions = 'where'

            if message_client_id is not None and where_conditions == 'where':
                where_conditions += f' id={message_client_id}'
            elif message_client_id is not None:
                where_conditions += f' and id={message_client_id}'

            if topic_name is not None and where_conditions == 'where':
                where_conditions += f' topic={topic_name}'
            elif topic_name is not None:
                where_conditions += f' and topic={topic_name}'

            if broker is not None and where_conditions == 'where':
                where_conditions += f' broker={broker}'
            elif broker is not None:
                where_conditions += f' and broker={broker}'
            headers['command'] += f' {where_conditions}'

        r, error = anylog_conn.get(headers=headers)
        if r is False and exception is True:
            rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            output = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    return output


def put_data(anylog_conn:AnyLogConnector, db_name:str, table_name:str, payloads:list, exception:bool=False):
    """
    Store data in AnyLog via PUT command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#using-a-put-command
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog va RESt
        db_name:str - logical database to store data in
        table_name:str - table to store data in (within logical database)
        payloads:lst - content to store in AnyLog (content will be converted from JSON dict to JSON string)
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status = True
    payloads = support.json_dumps(payloads, indent=4, exception=exception)
    headers = {
        'type': 'json',
        'dbms': db_name,
        'table': table_name,
        'Content-Type': 'text/plain'
    }

    r, error = anylog_conn.put(headers=headers, payload=payloads)
    if r is False:
        status = False
        if exception is True:
            rest_support.print_rest_error(call_type='PUT', cmd='data insertion', error=error)

    return status


def post_data(anylog_conn:AnyLogConnector, topic:str, payloads:list, exception:bool=False):
    """
    Store data in AnyLog via POST command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#using-a-post-command
    :note:
        `run mqtt client` is required to properly data in AnyLog
    :args:
        anylog_conn:AnyLogConnector - connecton to AnyLog va RESt
        topic:str - topic to be used when posting data
        payloads:lst - content to store in AnyLog (content will be converted from JSON dict to JSON string)
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status = True
    payloads = support.json_dumps(payloads, indent=4, exception=exception)
    headers = {
        'command': 'data',
        'topic': topic,
        'User-Agent': 'AnyLog/1.23',
         'Content-Type': 'text/plain'
    }

    r, error = anylog_conn.post(headers=headers, payloads=payloads)
    if r is False:
        status = False
        if exception is True:
            rest_support.print_rest_error(call_type='POST', cmd='data insertion', error=error)

    return status


def run_mqtt_client(anylog_conn:AnyLogConnector, broker:str, port:int, username:str=None, password:str=None,
                    topic:str='*', db_name:str=None, table_name:str=None, timestamp:str='timestamp', values:dict={},
                    logs:bool=False, user_agent:bool=False, view_help:bool=False, exception:bool=False):
    """
    Generate `run mqtt client` command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/message%20broker.md#subscribing-to-a-third-party-broker
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node via REST
        broker:str - broker connection information
        port:int port associated with broker
        username:str - username credentials for broker
        password:str - password for username
        topic:str - specific topic to work against (if '*' then assumes all topic names)
        db_nmae:str - logical database name
        table_name:str - table name
        timestamp:str - timestamp column
        value:dict - dict of key/value pairs (ex. {'value': 'value'} || {'value': {'type': 'int', 'value': 'value'}}
                     if no type is set, uses string (str)
        logs:bool - whether to print MQTT logs
        user_agent:bool - whether to use user-agent in `run mqtt`. if `broker` == rest sets to True by default
        view_help:bool - whether to print help information
        exception:bool - whether to print exception information
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status = None
    headers = {
        'command': f'run mqtt client where broker={broker} and port={port}',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        status = True
        headers['command'] = generic_data_support.generate_run_mqtt_client(broker=broker, port=port, username=username,
                                                                           password=password, topic=topic,
                                                                           db_name=db_name, table_name=table_name,
                                                                           timestamp=timestamp, values=values,
                                                                           logs=logs, user_agent=user_agent)
        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def set_partitions(anylog_conn:AnyLogConnector, db_name:str, table_name:str='*', partition_column:str='timestamp',
                   partition_interval:str='day', view_help:bool=False, exception:bool=False):
    """
    Set partitions
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#partition-command
    :args:
        anylog_conn:AnyLogConnection - connect to AnyLog via REST
        db_name:str - database to partition
        table_name:str - table to partition if '*' then partition all correlated tables
        partition_column:str - partition column
        partition_interval:str - partition interval
        view_help:bool - whether to print help
        exceptions:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status = None
    headers = {
        'command': 'partition',
        'User-Agent': 'AnyLog/1.23'
    }

    if view_help is True:
        generic_get_calls.help_command(headers=headers['command'])
    else:
        status = True
        headers['command'] += f' {db_name} {table_name} using {partition_column} by {partition_interval}'
        r, error = anylog_conn.post(headers=headers)
        if r is False:
            status = False
            if exception is True:
                rest_support.print_rest_error(call_type='POST', cmd=headers['command'], error=error)

    return status


def query_data(anylog_conn:AnyLogConnector, db_name:str, query:str, destination:str='network', format:str='json',
               stat:bool=True, include:str=None, extend:str=None, timezone:str='local', view_help:bool=False,
               exception:bool=False):
    """
    SQL query execution via REST
    :url: 
        https://github.com/AnyLog-co/documentation/blob/master/queries.md
    :args; 
        anylog_conn:AnyLogConnector - connection to AnyLog via REST 
        db_name:str - logical database to query against 
        query:str - query to execute (ex. select count(*) from rand_datq where timestamp >= NOW() - 1 day) 
        destination:str - whether to run query against the entire network or specific node(s). If set to None, then
                          run without `destination`
        format:str - result fromat (json || table)
        stat:bool - whether to print statistics at the end of the query
                    to return results in true JSON format - stat should be set to False
        include:str  - comma separated "list" of tables to include in query
        extend:str -   comma separated "list" of information to include in the results  
        timezone:str - results timezone (https://github.com/AnyLog-co/documentation/blob/master/queries.md#timezones)
        view_help:bool - whether to print help information 
        exception:bool - whether to print exceptions
    :params:
        output:str - content to return
        command:str - generated command
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        return query results, if help is set or query query fails returns None
    """
    output = None
    if view_help is True:
        generic_get_calls.help_command(anylog_conn=anylog_conn, command='sql', exception=exception)
    else:
        headers = {
            'command': generic_data_support.generate_query(db_name=db_name, query=query, format=format, stat=stat,
                                                           include=include, extend=extend, timezone=timezone),
            'User-Agent': 'AnyLog/1.23'
        }
        if destination is not None:
            headers['destination'] = destination

        r, error = anylog_conn.get(headers=headers)
        if r is False:
            if exception is True:
                rest_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            output = rest_support.extract_results(cmd=headers['command'], r=r, exception=exception)

    return output

