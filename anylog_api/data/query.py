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
                           other_columns:Union[dict,list]=None, ts_min:bool=True, ts_max:bool=True, calc_min:bool=True,
                           calc_avg:bool=True, calc_max:bool=True, row_count:bool=False, where_condition:str=None,
                           order_by:str=None, limit:int=0, exception:bool=False)->str:
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

    group_by=[]
    increments_cmd = f"increments(%s, {int(units)}, {date_column})"
    if check_interval(time_interval, exception) is True:
        increments_cmd = increments_cmd % time_interval
    else:
        raise ValueError(f"Interval value {time_interval} - time interval options: second, minute, day, month or year")

    cmd = f"SELECT {increments_cmd}, "

    # timestamp
    if all(param is False for param in [ts_min, ts_max]):
        if exception is True:
            raise ValueError('Unable to generate query without an aggregate on timestamp column')
    if ts_min is True:
        cmd += f" min({date_column}) as min_{date_column}, "
    if ts_max is True:
        cmd += f" max({date_column}) as max_{date_column}, "
    if row_count is True:
        cmd += f"count({date_column}) as row_count, "

    # other columns
    for column in other_columns:
        if isinstance(other_columns, dict) and other_columns[column] in ['int', 'float']:
            if all(key is False for key in [calc_min, calc_max, calc_avg]):
                group_by.append(column)
                if exception is True:
                    warnings.warn(f'Grouping by numeric values')
            if calc_min is True:
                cmd += f" min({column}) as min_{column}, "
            if calc_avg is True:
                cmd += f" avg({column}) as avg_{column}, "
            if calc_max is True:
                cmd += f" max({column}) as max_{column}, "
        else:
            cmd += f"{column}, "
            group_by.append(column)

    cmd += cmd.rsplit(',', 1)[0] + f" FROM {table_name}"
    cmd += f" WHERE {where_condition}" if where_condition is not None else ""
    cmd += f" GROUP BY {','.join(group_by)}" if len(group_by) > 0 else ""
    if order_by:
        cmd += f"ORDER BY min_{date_column}" + f", {','.join(group_by)} {order_by}" if group_by else f" {order_by}"
    cmd += f" LIMIT {limit};" if limit > 0  else ";"

    return cmd


def build_period_query(table_name:str, time_interval:str, units:int, date_column:str, start_date:str='NOW()',
                       other_columns:list=None, where_condition:str=None, group_by:list=None, order_by:str=None,
                       limit:int=0, exception:bool=False)->str:
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
    period_function=f"period(%s, {units}, '{start_date}', {date_column})"
    if check_interval(time_interval, exception) is True:
        period_function = period_function % time_interval
    else:
        raise ValueError(f"Interval value {time_interval} - time interval options: second, minute, day, month or year")
    if start_date.lower() != 'now()' and __check_timestamp(start_date=start_date) is False:
        raise ValueError(f'Invalid start_timestamp value, cannot continue. Accepted Values: {",".join(FORMATS)}')

    cmd = f"SELECT {date_column}" + f", {', '.join(other_columns)} FROM {table_name}" if other_columns is not None else f" FROM {table_name}"

    cmd += f" WHERE {period_function}" + f" and ({where_condition})" if where_condition is not None else ""
    cmd += f" GROUP BY {','.join(group_by)}" if group_by is not None and len(group_by) > 0  else ""
    cmd += f" ORDER BY {date_column} {order_by}" if order_by.lower() in ['asc', 'desc'] else ""
    cmd += f" LIMIT {limit};" if limit > 0 else ";"

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
        "command": "",
        "User-Agent": "AnyLog/1.23",
        "destination": destination
    }
    command = f'sql {db_name}'

    command += f"sql {db_name} "
    command += f" format={output_format.lower()} and " if output_format.lower() in ['json', 'table', 'json:list', 'json:output'] else ""
    command += f" stat={str(stat).lower()}" if isinstance(stat, bool) else ""
    command += f" timezone={timezone}" if timezone else ""
    command += f" include={tuple(','.join(include))} and" if isinstance(include, (list, tuple)) and len(include) > 0 else ""
    command += f" extend={tuple(','.join(extend))} and" if isinstance(extend, (list, tuple)) and len(extend) > 0 else ""
    command = command.strip().rsplit('and', 1)[0].strip() if command.strip().split()[-1] == 'and' else command.strip()
    headers['command'] += f'{command} "{sql_query}"'

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output  = headers['command']
    else:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output



