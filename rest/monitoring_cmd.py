import import_packages
import_packages.import_dirs()

import anylog_api
import other_cmd

HEADERS = {
    "command": None,
    "User-Agent": "AnyLog/1.23"
}


def set_monitor_streaming_data(conn:anylog_api.AnyLogConnect, db_name:str, table_name:str='*', intervals:int=10,
                           frequency:str='1 minute', value_col:str='value', exception:bool=False)->bool:
    """
    Track data streamed to a node for storage and processing
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20data.md
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog via REST
        db_name:str - The name of the database that hosts the table's data.
        table_name:str  - The data table name. If table name is not provided, all the tables associated to the database
                          are monitored using the database definitions.
        intervals:str - The number of intervals to keep
        frequency - The length of the interval expressed in one of the following: seconds, minutes, hours, days.
        value_col:str - The name of the column being monitored (the column name in the tablr that hosts the data).
    :params:
        status:bool
        cmd:str - command to execute
        HEADER:dict - REST header information
    :return:
        status
    """
    status = True
    cmd = "data monitor where dbms=%s" % db_name

    # must specify a single table - otherwise will accept all tables
    if table_name != '*' and ',' not in table_name and not isinstance(table_name, list):
        cmd += " and table=%s" % table_name
    cmd += " and intervals=%s and time=%s and value_column=%s" % (intervals, frequency, value_col)

    HEADERS['command'] = cmd

    r, error = conn.post(headers=HEADERS)
    if other_cmd.print_error(conn=conn.conn, request_type='post', command=cmd, r=r, error=error, exception=exception):
        status = False
    return status

