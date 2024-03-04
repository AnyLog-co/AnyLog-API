from anylog_api.anylog_connector import AnyLogConnector
from anylog_api.generic_get import __generic_execute as generic_get


def query_data(anylog_conn:AnyLogConnector, db_name:str, query:str, output_format:str='json', statistics:bool=True,
               include:tuple=(), extend:tuple=(), timezone:str='local', destination:str='network',
               print_output:bool=False, view_help:bool=False, exception:bool=False):
    """
    Query data against the network
    :command:
        sql test format=table "select count(*) from sample_data"
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/queries.md
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        db_name:str - database to query against
        query:str - SELECT statement
        output_format:str - format to return data json or table
        statistics:bool - whether to return query stats
        include:tuple - Allows to treat remote tables with a different name as the table being queried. The value is specified as dbms.table
        extend:tuple - Include node variables (which are not in the table data) in the query result set. Example: extend = (@ip, @port.str, @DBMS, @table, !disk_space.int).
        timezone:str - Timezone used for time values in the result set
        destination:str - remote machine IP and Port
        print_output:bool - whether to print results from executed command
        view_help:bool - print help information
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST information
        query_generator:str - generated query
    :return:
        query result
    """
    # build query
    if output_format.lower() not in ['json', 'table']:
        output_format = 'json'
        if exception is True:
            print(f"Setting output to default value JSON due to invalid output format {output_format}; valid formats are table and JSON")
    query_generator = f"sql {db_name} format={output_format.lower()}"
    if statistics is False:
        query_generator += " and stat=false"
    if include != ():
        include = str(include).replace("'", "").replace('"', '')
        query_generator += f" and include={include}"
    if extend != ():
        extend = str(extend).replace("'", "").replace('"', '')
        query_generator += f" and extend={extend}"
    if timezone:
        query_generator += f" and timezone={timezone}"
    query_generator += f" {query}"

    headers = {
        'command': query,
        'User-Agent': 'AnyLog/1.23'
    }
    if destination:
        headers['destination'] = destination

    return generic_get(anylog_conn=anylog_conn, headers=headers, view_help=view_help, print_output=print_output, exception=exception)


def query_status(anylog_conn:AnyLogConnector, query_id:int=None, destination:str=None, print_output:bool=False, view_help:bool=False, exception:bool=False):
    """
    Get query status
    :command:
        query status
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/profiling%20and%20monitoring%20queries.md#identifying-slow-queries
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        query_int:int - specific query ID
        destination:str - remote machine IP and Port
        print_output:bool - whether to print results from executed command
        view_help:bool - print help information
        exception:bool - whether to print exceptions
    :params:
       headers:dict - REST information
    :return:
        results for query status
    """
    headers = {
        'command': 'query status',
        'User-Agent': 'AnyLog/1.23'
    }

    if destination is not None:
        headers['destination'] = destination

    if query_id is not None:
        headers += f" {query_id}"

    return generic_get(anylog_conn=anylog_conn, headers=headers, print_output=print_output, view_help=view_help, exception=exception)


def query_time(anylog_conn:AnyLogConnector, destination:str=None, print_output:bool=False, view_help:bool=False, exception:bool=False):
    """
    summary of the execution time of queries
    :command:
        query time
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/profiling%20and%20monitoring%20queries.md#statistical-information
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        destination:str - remote machine IP and Port
        print_output:bool - whether to print results from executed command
        view_help:bool - print help information
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST information
    :return:
        query time
    """
    headers = {
        "command": "query time",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination

    return generic_get(anylog_conn=anylog_conn, headers=headers, print_output=print_output, view_help=view_help, exception=exception)