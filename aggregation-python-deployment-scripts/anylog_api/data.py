"""
Data related functions
:aggregation:
    - set aggregation
    - set ingestion
    - set encoding
    - get status for each (todo)
"""
from anylog_api.generic_rest import RestConn


def set_aggregation(conn:RestConn|None, db_name:str, table_name:str, value_column:str="*",
                    time_column:str="insert_timestamp", intervals:int=10, interval_time:str="1 minute",
                    keep_aggregation:bool=False, target_dbms:str=None, target_table:str=None,
                    return_cmd:bool=False, execute_cmd:bool=True, get_help:bool=False)->str|None:
    """
    Set aggregation on a specific table / column
    :args:
        conn:RestConn - connection to AnyLog / EdgeLake
        db_name:str - logical database name
        table_name:str - logical table name
        value_column:str - column to aggregate against
        time_column:str - timestamp column to aggregate with
        intervals:int - number of aggregations to keep
        interval_time:str - time period for each interval
        keep_aggregation:bool - keep aggregations
        target_dbms:str - target database for aggregation
        target_table:str - target table for aggregation
        return_cmd:bool - return command being executed
        execute_cmd:bool - execute command
        get_help:bool - print help for `set aggregation` instead of running command
    :params:
        headers:dict - REST headers
    :print:
        if get_help - print explanation for command
    """
    headers = {
        "command": f"""set aggregation where 
            dbms={db_name} and 
            table={table_name} and 
            time_column={time_column} and
            value_column={value_column} and
            intervals={intervals} and
            time={interval_time}""".replace("\n", " ").replace("\t", " ").strip(),
        "User-Agent": "AnyLog/1.23"
    }


    if keep_aggregation:
        headers["command"] += f" and target_dbms={target_dbms}" if target_dbms is None else f" and target_dbms=agg_{db_name}"
        if target_table is None and value_column != "value":
            headers["command"] = f" and target_table={table_name.strip()}_{value_column.strip()}"
        elif target_table is None:
            headers["command"] = f" and target_table={table_name.strip()}"
        else:
            headers["command"] += f" and target_table={target_table}"

    if get_help:
        conn.get_help(command=headers["command"])
    if execute_cmd:
        conn.execute_post(headers=headers)
    if return_cmd:
        return headers["command"]
    print(headers["command"])


def set_ingestion(conn:RestConn, db_name:str, table_name:str="*", keep_source:bool=True, keep_aggregation:bool=False,
                  return_cmd:bool=False, execute_cmd:bool=True, get_help:bool=False):
    """
    Set data ingestion - whether to only raw content, aggregation or both
    :args:
        conn:RestConn - connection to AnyLog / EdgeLake
        db_name:str - logical database name
        table_name:str - logical table name
        keep_source:bool - keep source data
        keep_aggregation:bool  - keep aggregation data
        return_cmd:bool - return command being executed
        execute_cmd:bool - execute command
        get_help:bool - print help for `set aggregation` instead of running command
    :params:
        headers:dict - REST headers
    :print:
        if get_help - print explanation for command
    """
    headers  = {
        "command": f"""set aggregation ingest where 
            dbms={db_name} and 
            table={table_name} and 
            source={'true' if keep_source else 'false'} and
            derived={'true' if keep_aggregation else 'false'}""".replace("\n", " ").replace("\t", " ").strip(),
        "User-Agent": "AnyLog/1.23"
    }

    if get_help:
        conn.get_help(command=headers["command"])
    if execute_cmd:
        conn.execute_post(headers=headers)
    if return_cmd:
        return headers["command"]
    # print(headers["command"])

def set_encoding(conn:RestConn, db_name:str, table_name:str, value_column:str, encoding=None,
                 return_cmd:bool=False, execute_cmd:bool=True, get_help:bool=False):
    """
    The command `set aggregations encoding` applies encoding on the values assigned to each time interval.
    :args:
        conn:RestConn - connection to AnyLog / EdgeLake
        db_name:str - logical database name
        table_name:str - logical table name
        value_column:str - value column to run encoding against
        encoding:str - encoding type
            * None - no encoding
            * bounds - all entries in the time interval are replaced with a single entry
            * arle - Approximated Run-Length Encoding, the entries in the time interval are represented in a sequence of entries.
        return_cmd:bool - return command being executed
        execute_cmd:bool - execute command
        get_help:bool - print help for `set aggregation` instead of running command
    :params:
        headers:dict - REST headers
    :print:
        if get_help - print explanation for command
    """
    headers = {
        "command": f"set aggregation encoding where dbms={db_name} and table={table_name} and value_column={value_column} {f' and encoding={encoding}' if encoding else ''}",
        "User-Agent": "AnyLog/1.23"
    }

    if get_help:
        conn.get_help(command=headers["command"])
    if execute_cmd:
        conn.execute_post(headers=headers)
    if return_cmd:
        return headers["command"]
    print(headers["command"])