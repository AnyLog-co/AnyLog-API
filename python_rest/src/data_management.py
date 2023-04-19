import pytz
import anylog_connector


def post_data(anylog_conn:anylog_connector.AnyLogConnector, topic:str, payload:str):
    """
    Publish data into AnyLog via POST command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#using-a-post-command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog
        topic:str - topic to publish data against
        payload:str - JSON string of data to publish
    :params:
        status:bool
        headers:dict - REST header information
        r:results.model.Response - request response
    :return:
        status
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


def put_data(anylog_conn:anylog_connector.AnyLogConnector, payload:str, db_name:str, table_name:str, mode:str="streaming"):
    """
    Store data into AnyLog via PUT
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#using-a-put-command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog
        payload:str - JSON string of data to publish
        db_name:str - logical database to store data
        table_name:str - table to store data in
        mode:streaming - format to ingest data (default: streaming)
            file - The body of the message is JSON data. Database load (on an Operator Node) and data send
                   (on a Publisher Node) are with no wait. File mode is the default behaviour.
            streaming - The body of the message is JSON data that is buffered in the node. Database load
                        (on an Operator Node) and data send (on a Publisher Node) are based on time and volume
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
    :return:
       status
    """
    status = True
    headers = {
        'type': 'json',
        'dbms': db_name,
        'table': table_name,
        'Content-Type': 'text/plain'
    }

    if mode in ["streaming", "file"]:
        headers["mode"] = mode
    else:
        headers["mode"] = "streaming"

    if status is True:
        r = anylog_conn.put(headers=headers, payload=payload)
        if r is None or int(r.status_code) != 200:
            status = False

    return status


def query_data(anylog_conn:anylog_connector.AnyLogConnector, db_name:str, sql_query:str, format:str="json",
               timezone:str="local", include:str=None, extend:str=None, stat:bool=True, dest:str=None,
               file_name:str=None, table:str=None, test:bool=False, source:str=None, title:str=None,
               destination:str='network', view_help:bool=False):
    """
    Execute query against AnyLog
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/queries.md#query-nodes-in-the-network
    :args:
        anylog_conn:anylog_connector.AnyLogConnector, - connection to AnyLog via REST
        db_name:str - database to query against
        sql_query:str - "SELECT" command to execute
        format:str - The format of the result set
        timezone:str - Timezone used for time values in the result set
            A full list can be found: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        include:list - Allows to treat remote tables with a different name as the table being queried. The value is
                       specified as dbms.table
        extend:list - Include node variables (which are not in the table data) in the query result set.
                      Example: extend = (@ip, @port.str, @DBMS, @table, !disk_space.int).
        stat:bool - Adds processing statistics to the query output
        dest:str - Destination of the query result set (i.e. stdout, rest, file)
        file_name:str - File name for the output data
        table:str - A table name for the output data (random table names are assigned to each executing query)
        test:bool - The output is organized as a test output
        source:str - A file name that is used in a test process to determine the processing result
        title:str - Added to the test information in the test header
        destination:str - where to query against
    :params:
        sql_cmd:str - generated full `sql` command
    :return:
        if view_help is True - return None
        else returns results
    """
    sql_cmd = f'sql {db_name} format={format} and timezone={timezone} and stat=true'

    if format not in ["json", "table"]:
        sql_cmd.replace(format, "json")
    if timezone not in pytz.all_timezones and timezone != "local":
        sql_cmd.replace(timezone, "local")
    if stat is False:
        sql_cmd.replace("stat=true", "stat=false")

    if include is not None:
        sql_cmd += f" and include=("
        for param in include.split(','):
            sql_cmd += param
            if param != include.split(',')[-1]:
                sql_cmd += ","
            else:
                sql_cmd += ")"
    if extend is not None:
        sql_cmd += f" and extend=("
        for param in extend.split(','):
            sql_cmd += param
            if param != extend.split(',')[-1]:
                sql_cmd += ","
            else:
                sql_cmd += ")"

    if dest in ["stdout", "rest", "dbms", "file"]:
        sql_cmd += f" and dest={dest}"
    if file_name is not None:
        sql_cmd += f" and file={file_name}"
    if table is not None:
        sql_cmd += f" and table={table}"
    if test is True:
        sql_cmd += f" and test=true"
    if source is not None:
        sql_cmd += f" and source={source}"
    if title is not None:
        sql_cmd += f" and title={title}"

    sql_cmd += f' "{sql_query}"'

    headers = {
        "command": sql_cmd,
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None and destination != "":
        headers['destination'] = destination

    if view_help is True:
        anylog_connector.view_help(anylog_conn=anylog_conn, cmd=sql_query)
        return None

    return anylog_conn.get(headers=headers)
