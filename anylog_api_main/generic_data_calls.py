from anylog_connector import AnyLogConnector
import generic_get_calls
import generic_data_support
import rest_support
import support


def get_partitions(anylog_conn:AnyLogConnector, view_help:bool=False, exception:bool=False)->bool:
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







def set_partitions(anylog_conn:AnyLogConnector, db_name:str, table_name:str='*', partition_column:str='timestamp',
                   partition_interval:str='day', view_help:bool=False, exception:bool=False)->bool:
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
               exception:bool=False)->str:
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

