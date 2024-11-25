import datetime
import warnings
from typing import Union

import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.__support__ import check_interval

FORMATS = ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S',
               '%Y-%m-%d %H:%M', '%Y-%m-%d']

def __check_timestamp(start_date)->bool:
    """
    Check whether timestamp given in period is valid
    :args:
        start_date:str - datetime timestamp
    :global:
        FORMATS:list - List of formats supported
    :params:
        status:bool
    :return:
        status
    """
    status = False
    for frmt in FORMATS:
        try:
            datetime.datetime.strptime(start_date, frmt)
        except ValueError:
            pass
        else:
            status = True
            break

    return status


def build_increments_query(table_name:str, time_interval:str, units:int, date_column:str,
                           other_columns:Union[dict,list]=None, ts_min:bool=True, ts_max:bool=True,
                           row_count:bool=False, where_condition:str=None, order_by:str=None, limit:int=0,
                           exception:bool=False)->str:
    """
    The increments functions considers data in increments of time (i.e. every 5 minutes) within a time range
    (i.e. between 'October 15, 2019' and 'October 16, 2019').date-column is the column name of the column that determines
    the date and time to consider. The time-interval and units (of time-interval) determine the time increments to
    consider (i.e. every 2 days) and the time-range is determined in the where clause.
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/queries.md#the-increment-function
    :sample-query:
        SELECT
            increments(minute, 1, insert_timestamp), MIN(insert_timestamp) AS min_ts, MAX(insert_timestamp) AS min_ts,
            MIN(value) AS min_value, AVG(value) AS avg_value, MAX(value) AS max_value, COUNT(value) AS row_count
        FROM
            my_table
        WHERE
            insert_timestamp >= NOW() - 1 hour
        ORDER BY
            min_ts
    :args:
        table_name:str - the table to query against
        time_interval:str - time interval
            * seconds
            * minutes
            * hours
            * days
            * months
        units:int - units (of time-interval)
        date_column:str - timestamp column name
        other_columns:Union[dict, list] - other columns to utilize for query
            sample dict: {'str_variable': 'str', 'int_variable': 'int'}
            sample list: ['str_variable', 'min(int_variable)', 'max(int_variable)']
        calc_min:bool - when other_columns is in dict format and column type is int/float, add min(other_columns) to query
        calc_avg:bool - when other_columns is in dict format and column type is int/float, add avg(other_columns) to query
        calc_max:bool - when other_columns is in dict format and column type is int/float, add max(other_columns) to query
        row_count:bool - utilize date_column column to generate row count
        where_condition:str - WHERE condition
        order_by:str - ORDER BY based on timestamp and `GROUP BY`
            * desc
            * asc
        exception:bool - print exceptions
    :params:
        group_by:list - based on the way the query is built, columns to group by
        increments_cmd:str - generated  increments command
        cmd:str - generated command
    :return:
        cmd
    """
    if not table_name or not time_interval or not date_column:
        raise ValueError("Table name, time interval, and date column must be specified.")

    if time_interval not in ['second', 'minute', 'hour', 'day', 'month', 'year']:
        raise ValueError(
            f"Invalid time interval: {time_interval}. Must be one of: second, minute, hour, day, month, year.")

    if not isinstance(units, int) or units <= 0:
        raise ValueError("Units must be a positive integer.")

    # Base increments function
    increments_cmd = f"increments({time_interval}, {units}, {date_column})"
    cmd = f"SELECT {increments_cmd}, "

    # Add timestamp aggregations
    if not ts_min and not ts_max and not row_count:
        if exception:
            raise ValueError("At least one of ts_min, ts_max, or row_count must be True.")
    cmd += f"MIN({date_column}) AS min_{date_column}, " if ts_min else ""
    cmd += f"MAX({date_column}) AS max_{date_column}, " if ts_max else ""
    cmd += f"COUNT(*) AS row_count, " if row_count else ""

    # Process other_columns
    group_by = []
    if isinstance(other_columns, dict):
        for column, operations in other_columns.items():
            if not operations or "distinct" in operations:
                cmd += f"{column}, "
                group_by.append(column)
            if "min" in operations:
                cmd += f"MIN({column}) AS min_{column}, "
            if "max" in operations:
                cmd += f"MAX({column}) AS max_{column}, "
            if "avg" in operations:
                cmd += f"AVG({column}) AS avg_{column}, "
            if "sum" in operations:
                cmd += f"SUM({column}) AS sum_{column}, "
            if "distinct" in operations:
                cmd += f"DISTINCT({column}) AS distinct_{column}, "
            if "count_distinct" in operations:
                cmd += f"COUNT(DISTINCT({column})) AS count_distinct_{column}, "
    elif isinstance(other_columns, list):
        cmd += ", ".join(other_columns) + ", "

    # Clean trailing comma
    cmd = cmd.rstrip(", ")

    # Add FROM clause
    cmd += f" FROM {table_name}"

    # Add WHERE clause
    if where_condition:
        cmd += f" WHERE {where_condition}"

    # Add GROUP BY clause
    if group_by:
        cmd += f" GROUP BY {', '.join(group_by)}"

    # Add ORDER BY clause
    if order_by:
        cmd += " ORDER BY "
        if ts_min:
            cmd += f"min_{date_column}, "
        elif ts_max:
            cmd += f"max_{date_column}, "
        if group_by:
            cmd += f"{', '.join(group_by)}, "
        cmd = cmd.rstrip(", ")
        if order_by.lower() not in ['asc', 'desc']:
            if exception:
                raise ValueError("ORDER BY value must be 'asc' or 'desc'.")
        else:
            cmd += f" {order_by.upper()}"

    # Add LIMIT clause
    if limit > 0:
        cmd += f" LIMIT {limit}"

    # Finalize query
    cmd = cmd.strip() + ";"
    return cmd


def build_period_query(table_name:str, time_interval:str, units:int, date_column:str, start_date:str='NOW()',
                       other_columns:Union[dict, list]=None, ts_min:bool=False, ts_max:bool=False, row_count:bool=False,
                       where_condition:str=None, group_by:list=None, order_by:str=None, limit:int=0,
                       exception:bool=False)->str:
    """
    The period function finds the first occurrence of data before or at a specified date (and if a filter-criteria is
    specified, the occurrence needs to satisfy the filter-criteria) and considers the readings in a period of time which
    is measured by the type of the time interval (Minutes, Hours, Days, Weeks, Months or Years) and the number of units
    of the time interval (i.e. 3 days - whereas time-interval is day and unit is 3).
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/queries.md#the-period-function
    :sql:
        SELECT
            timestamp, value
        FROM
            my_table
        WHERE
            period(minute, 1, now(), timestamp)
    :args:
        table_name:str - logical table name
                time_interval:str - time interval
            * seconds
            * minutes
            * hours
            * days
            * months
        units:int - units (of time-interval)
        date_column:str - timestamp column name
        other_columns:Union[dict, list] - other columns to utilize for query
            sample list: ['str_variable', 'min(int_variable)', 'max(int_variable)']
        where_condition:str - WHERE condition
        group_by:list - list of columns to group by
        order_by:str - ORDER BY based on timestamp column
            * desc
            * asc
        exception:bool - print exceptions
    :global:
        FORMATS:list - List of formats supported
    :params:
        period_function:str - period function
        cmd:str - generated SELECT command
    :return:
        cmd
    """
    group_by = []
    period_function=f"period(%s, {units}, '{start_date}', {date_column})"
    if check_interval(time_interval, exception) is True:
        period_function = period_function % time_interval
    else:
        raise ValueError(f"Interval value {time_interval} - time interval options: second, minute, day, month or year")
    if 'now' not in start_date.lower() and __check_timestamp(start_date=start_date) is False:
        raise ValueError(f'Invalid start_timestamp value, cannot continue. Accepted Values: {", ".join(FORMATS)}')

    cmd = "SELECT "
    if all(param is False for param in [ts_min, ts_max]):
        cmd += f"{date_column}, "
        group_by.append(date_column)
    cmd += f"min({date_column}) as min_{date_column}, " if ts_min is True else ""
    cmd += f"max({date_column}) as max_{date_column}, " if ts_max is True else ""
    if isinstance(other_columns, dict):
        for column, operations in other_columns.items():
            if not operations or "distinct" in operations:
                cmd += f"{column}, "
                group_by.append(column)
            if "min" in operations:
                cmd += f"MIN({column}) AS min_{column}, "
            if "max" in operations:
                cmd += f"MAX({column}) AS max_{column}, "
            if "avg" in operations:
                cmd += f"AVG({column}) AS avg_{column}, "
            if "sum" in operations:
                cmd += f"SUM({column}) AS sum_{column}, "
            if "distinct" in operations:
                cmd += f"DISTINCT({column}) AS distinct_{column}, "
            if "count_distinct" in operations:
                cmd += f"COUNT(DISTINCT({column})) AS count_distinct_{column}, "
    elif isinstance(other_columns, list):
        cmd += ", ".join(other_columns) + ", "

    # Clean trailing comma
    cmd = cmd.rstrip(", ")

    # Add FROM clause
    cmd += f" FROM {table_name}"

    # Add WHERE clause
    cmd += f" WHERE {period_function} "
    cmd += f" and ({where_condition})" if where_condition else ""

    # Add GROUP BY clause
    if group_by:
        cmd += f" GROUP BY {', '.join(group_by)}"

    # Add ORDER BY clause
    if order_by:
        cmd += " ORDER BY "
        if ts_min:
            cmd += f"min_{date_column}, "
        elif ts_max:
            cmd += f"max_{date_column}, "
        if group_by:
            cmd += f"{', '.join(group_by)}, "
        cmd = cmd.rstrip(", ")
        if order_by.lower() not in ['asc', 'desc']:
            if exception:
                raise ValueError("ORDER BY value must be 'asc' or 'desc'.")
        else:
            cmd += f" {order_by.upper()}"

    # Add LIMIT clause
    if limit > 0:
        cmd += f" LIMIT {limit}"

    # Finalize query
    cmd = cmd.strip() + ";"
    return cmd


def query_data(conn:anylog_connector.AnyLogConnector, db_name:str, sql_query:str, output_format:str='json',
               stat:bool=True, timezone:str='local', include:list=None, extend:list=None, destination:str='network',
               view_help:bool=False, return_cmd:bool=False, exception:bool=False)->Union[str, dict, None]:
    """
    Execute query
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/queries.md
    :args:
        conn:anylog_connector.AnyLogConnector - Connection to AnyLog
        db_name:str - logical database name
        sql_query:str - query to execute
        output_format:str - The format of the result set
            * table
            * json
            * json:list
            * json:output
        stat:bool - Adds processing statistics to the query output
        timezone:str - Timezone used for time values in the result set
        include:list - Allows to treat remote tables with a different name as the table being queried. The value is specified as dbms.table
        extend:list - Include node variables (which are not in the table data) in the query result set. Example: extend = (@ip, @port.str, @DBMS, @table, !disk_space.int).
        destination:str - Remote node to query against
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        output
        headers:dict - REST header information
    :return:
        if return_cmd is True -> return cmd
        else -> return query result
    """
    headers = {
        "command": f'sql {db_name}',
        "User-Agent": "AnyLog/1.23",
        "destination": destination
    }

    headers['command'] += f" format={output_format.lower()} and" if output_format.lower() in ['json', 'table', 'json:list', 'json:output'] else ""
    headers['command'] += f" stat={str(stat).lower()} and" if isinstance(stat, bool) else ""
    headers['command'] += f" timezone={timezone} and" if timezone else ""
    headers['command'] += f" include={tuple(','.join(include))} and" if isinstance(include, (list, tuple)) and len(include) > 0 else ""
    headers['command'] += f" extend={tuple(','.join(extend))} and" if isinstance(extend, (list, tuple)) and len(extend) > 0 else ""
    headers['command'] = headers['command'].strip().rsplit('and', 1)[0].strip() if headers['command'].strip().split()[-1] == 'and' else headers['command'].strip()
    headers['command'] += f' "{sql_query}"'

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output  = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output



