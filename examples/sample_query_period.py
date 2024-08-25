"""
Sample Configs:
    23.239.12.151:32349 litsanleandro ping_sensor --output-format table --time-column insert_timestamp --values timestamp,value --where-conditions "parentelement='1ab3b14e-93b1-11e9-b465-d4856454f4ba'" --return-cmd
    23.239.12.151:32349 litsanleandro ping_sensor --time-column timestamp --interval day --time-units 1 --values device_id,count(*) --group-by device_id --output-format table
"""

import argparse
import anylog_api.anylog_connector as anylog_connector
import anylog_api.generic.get as generic_get
import anylog_api.data.query as query_data
import __support__ as support


def main():
    """
    Send data via POST - REST
    :positional arguments:
        conn:str        connection information to send data into AnyLog/EdgeLake
        db_name:str     logical database name
        table:str       physical table name
    :options:
        -h, --help                      show this help message and exit
        --time-column   TIME_COLUMN     timestamp column to query against
        --interval      INTERVAL        time interval for query
            second
            minute
            hour
            day
            week
            month
            year
        --time-units    TIME_UNITS      numerical value for time interval
        --values        VALUES          comma sepeerated list of values
        --where-conditions  WHERE_CONDITIONS        User defined where conditions
        --group-by          GROUP_BY
        --order-by          ORDER_BY              whether to enable order by (min / max) timestamp
        --limit             LIMIT                   limit number of rows to return. if set to 0, then no limit
        --output-format     OUTPUT_FORMAT           SQL request output format
            json
            table
            json:list
        --stat              [STAT]                  whether to return statistics
        --timezone          TIMEZONE                Result timezone
        --include           INCLUDE                 list of tables to query against
        --extend            EXTEND                  blockchain info to include in results
        --timeout           TIMEOUT                 REST request timeout
        --view-help         [VIEW_HELP]             get help on command
        --return-cmd        [RETURN_CMD]            return generated command
        --exception         [EXCEPTION]             Whether to print exceptions
    :params:
        conn:str - REST IP:Port
        auth:tuple - REST authentication
        anylog_conn:anylog_connector.AnyLogConnector - REST connection information
        payloads:list - data to insert
    """
    parse = argparse.ArgumentParser()
    parse.add_argument("conn", type=support.check_conn, default="127.0.0.1:32149",
                       help="Connection information to send data into AnyLog/EdgeLake")
    parse.add_argument("db_name", type=str, default="test", help="logical database name")
    parse.add_argument("table_name", type=str, default="sample_data", help="physical table name")
    parse.add_argument("--time-column", type=str, default='insert_timestamp', help='timestamp column to query against')
    parse.add_argument('--interval', type=str, default='minute',
                       choices=['second', 'minute', 'hour', 'day', 'week', 'month', 'year'],
                       help='time interval for query')
    parse.add_argument('--time-units', type=int, default=1, help='numerical value for time interval')
    parse.add_argument('--values', type=str, default='value', help='comma sepeerated list of values')
    parse.add_argument('--start-timestamp', type=str, default='NOW()', help='start timestamp')
    parse.add_argument('--where-conditions', type=str, default=None, help='User defined where conditions')
    parse.add_argument('--group-by', type=str, default=None, help='comma separated values to group by')
    parse.add_argument('--order-by', type=str, default=None, help='comma separated values to order by (with asc/desc)')
    parse.add_argument('--limit', type=int, default=0, help='limit number of rows to return. if set to 0, then no limit')

    parse.add_argument('--output-format', type=str, choices=['json', 'table', 'json:list'], default='json', help='SQL request output format')
    parse.add_argument('--stat', type=bool, default=True, const=False, nargs='?', help='whether to return statistics')
    parse.add_argument('--timezone', type=str, default=None, help='Result timezone')
    parse.add_argument('--include', type=str, default=None, help="list of tables to query against")
    parse.add_argument('--extend', type=str, default=None, help='blockchain info to include in results')

    parse.add_argument("--timeout", type=float, default=30, help="REST request timeout")
    parse.add_argument('--view-help', type=bool, default=False, const=True, nargs='?', help="get help on command")
    parse.add_argument('--return-cmd', type=bool, default=False, const=True, nargs='?', help="return generated command")
    parse.add_argument('--exception', type=bool, default=False, const=True, nargs='?',
                       help="Whether to print exceptions")
    args = parse.parse_args()

    # validate node is accessible
    conn, auth = next(iter(args.conn.items()))
    anylog_conn = anylog_connector.AnyLogConnector(conn, auth=auth, timeout=args.timeout)
    if generic_get.get_status(conn=anylog_conn, destination=None, view_help=False, return_cmd=False,
                              exception=args.exception) is False:
        print(f"Failed to communicated with {anylog_conn.conn}. cannot continue...")
        exit(1)

    values = args.values.strip().split(",")

    # period query
    sql_query = query_data.build_period_query(table_name=args.table_name, time_interval=args.interval, units=args.time_units,
                                              time_column=args.time_column, value_columns=args.values, start_ts='NOW()',
                                              where_conditions=args.where_conditions, group_by=args.group_by,
                                              order_by_columns=args.order_by, limit=args.limit,
                                              exception=args.exception)

    output = query_data.query_data(conn=anylog_conn, db_name=args.db_name, sql_query=sql_query, output_format=args.output_format,
                                   stat=args.stat, timezone=args.timezone, include=args.include, extend=args.extend,
                                   view_help=args.view_help, return_cmd=args.return_cmd, exception=args.exception)

    if output['command'] is not None and args.view_help is False:
        print(output['command'], "\n")
    if output['results'] is not None:
        print(output['results'])


if __name__ == '__main__':
    main()