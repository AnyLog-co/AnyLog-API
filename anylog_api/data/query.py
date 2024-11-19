"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""

import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.__support__ import check_interval


def build_increments_query(table_name:str, time_interval:str, units:int, time_column:str, value_columns,
                           calc_min:bool=True, calc_avg:bool=True, calc_max:bool=True, row_count:bool=True,
                           where_condition:str=None, order_by:bool=True, limit:int=0, exception:bool=False)->str:
    """
    The increments functions considers data in increments of time (i.e. every 5 minutes) within a time range
    (i.e. between October 15, 2019 and October 16, 2019).date-column is the column name of the column that determines
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
        table_name:str - logical table name
        time_interval:str - time interval (second, minute, hour, day, week, month, year)
        unit:int - value for time interval
        time_column:str - timestamp column name
        value_columns - list or string of non-timestamp value column name
        calc_min:bool - calculate min value
        calc_avg:bool - calculate avg value
        calc_max:bool - calculate max value
        row_count:bool - calculate row count
        where_condition:str - user defined where condition
        order_by:bool - whether to enable order by (min / max) timestamp
        limit:int - limit number of rows to return. if set to 0, then no limit
    :params:
        sql_cmd:str - generated sql
    :return:
        sql_cmd
        if time_interval not met --> ""
    """
    group_by = []
    if check_interval(time_interval=time_interval, exception=exception) is False:
        return ""
    if not time_column:
        if exception is True:
            raise KeyError(f"Missing timestamp column name")
        return ""

    sql_cmd = f"SELECT increments({time_interval}, {units}, {time_column}), "
    if all(False is x for x in [calc_min, calc_max]):
        sql_cmd += f"MIN({time_column}) AS min_ts, MAX({time_column}) AS max_ts, "
    if calc_min is True:
        sql_cmd += f"MIN({time_column}) AS min_ts, "
    if calc_max is True:
        sql_cmd += f"MIN({time_column}) AS max_ts, "

    if value_columns and not isinstance(value_columns, list):
        value_columns = value_columns.split(",")
    if value_columns:
        for value_column in value_columns:
            if calc_min is True:
                sql_cmd += f"MIN({value_column}) AS min_{value_column}, "
            if calc_max is True:
                sql_cmd += f"MAX({value_column}) AS max_{value_column}, "
            if calc_avg is True:
                sql_cmd += f"AVG({value_column}) AS avg_{value_column}, "
            if all(x is False for x in [calc_min, calc_max, ]):
                sql_cmd += f"{value_column}, "
                group_by.append(value_column)
            if value_column != value_columns[-1]:
                sql_cmd += ", "

    if row_count is True:
        sql_cmd += f" COUNT(*) AS row_count "

    sql_cmd += f' FROM {table_name} '

    if where_condition:
        sql_cmd += f"WHERE {where_condition} "
    if group_by:
        sql_cmd += "GROUP BY "
        for value in group_by:
            sql_cmd += f"{value_column}"
            if value != group_by[-1]:
                sql_cmd += ", "
    if order_by is True:
        sql_cmd += " ORDER BY min_ts"
        if calc_min is False:
            sql_cmd = sql_cmd.replace('ORDER BY min_ts', 'ORDER BY max_ts')
    if limit > 0:
        sql_cmd += f" limit {limit}"

    return sql_cmd


def build_period_query(table_name:str, time_interval:str, units:int, time_column:str, value_columns:list,
                       start_ts='NOW()', where_conditions:str=None, group_by:str=None, order_by_columns:str=None, limit:int=0,
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
        time_interval:str - time interval (second, minute, hour, day, week, month, year)
        unit:int - value for time interval
        time_column:str - timestamp column name (used in period function)
        value_columns:list - list or string of value column names
        start_ts:str - start timestamp
        where_condition:str - user defined where condition
        group_by:str - comma - separated values to group by
        order_by_columns:str - comma separated values to order by (with asc/desc)
        exception:bool - print exception
    :params:
        sql_cmd:str - generated sql
    :return:
        sql_cmd
        if time_interval not met --> ""
    """
    if check_interval(time_interval=time_interval, exception=exception) is False:
        return ""
    if not time_column:
        if exception is True:
            raise KeyError(f"Missing timestamp column name")
        return ""

    period_cmd = f"period({time_interval}, {units}, {start_ts},{time_column})"
    sql_cmd = "select "

    if type(value_columns) not in [tuple, list]:
        value_columns = value_columns.strip().split(",")
    for value_column in value_columns:
        sql_cmd += f"{value_column},"

    sql_cmd = sql_cmd.rsplit(",", 1)[0] + f" FROM {table_name} WHERE {period_cmd}"

    if where_conditions:
        sql_cmd += f" and {where_conditions}"

    if group_by:
        sql_cmd += f" GROUP BY {group_by}"
    if order_by_columns:
        sql_cmd += f" ORDER BY {order_by_columns}"
    if limit > 0 :
        sql_cmd += f" limit {limit}"

    return sql_cmd


def query_data(conn:anylog_connector.AnyLogConnector, db_name:str, sql_query:str, destination:str='network',
               output_format:str='json', stat:bool=True, timezone:str=None, include:list=[], extend:list=[],
               view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    headers = {
        "command": f'sql {db_name}',
        "User-Agent": "AnyLog/1.23",
        "destination": destination
    }

    if extend:
        if isinstance(extend, list) or isinstance(extend, tuple):
            headers['command'] = headers['command'].replace(db_name, f"{db_name} extend=({','.join(extend)}) and")
        else:
            headers['command'] = headers['command'].replace(db_name, f"{db_name} extend=({extend}) and")
    if include:
        if isinstance(include, list) or isinstance(include, tuple):
            headers['command'] = headers['command'].replace(db_name, f"{db_name} extend=({','.join(include)}) and")
        else:
            headers['command'] = headers['command'].replace(db_name, f"{db_name} include=({include}) and")
    if timezone:
        headers['command'] = headers['command'].replace(db_name, f"{db_name} timezone={timezone} and")
    if stat is False:
        headers['command'] = headers['command'].replace(db_name, f"{db_name} stat=false and")
    if output_format in ['json', 'table', 'json:list']:
        headers['command'] = headers['command'].replace(db_name, f"{db_name} format={output_format} and")
    headers['command'] = headers['command'].rsplit('and', 1)[0] + " " + sql_query

    output = {"command": None, "results": None}
    if view_help is True:
        if return_cmd is True:
            print(headers['command'], "\n")
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    else:
        output['results'] = extract_get_results(conn=conn, headers=headers, exception=exception)
        if return_cmd is True:
            output['command'] = headers['command']

    return output
