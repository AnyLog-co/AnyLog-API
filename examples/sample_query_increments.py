"""
Sample Configs:
    10.0.0.228:2049 test rand_data --time-column timestamp --where-conditions "timestamp >= NOW() - 2 hours and timestamp <= NOW() - 1 hour" --limit 10 --order-by
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
        conn    Connection information to send data into AnyLog/EdgeLake
    :options:
        -h, --help                      show this help message and exit
        --db-name       DB_NAME         logical database name
        --table-name    TABLE_NAME      physical table name
        --total-rows    TOTAL_ROWS      number of rows to generate
        --wait-time     WAIT_TIME       How long to wait between each row
        --publish-mode {streaming,file} Publishing mode
        --timeout       TIMEOUT         REST request timeout
        --exception     [EXCEPTION]     Whether to print exceptions
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

    parse.add_argument('--disable-calc-min', type=bool, const=False, nargs='?', default=True,
                       help='disable calculating minimum value(s)')
    parse.add_argument('--disable-calc-avg', type=bool, const=False, nargs='?', default=True,
                       help='disable calculating average value(s)')
    parse.add_argument('--disable-calc-max', type=bool, const=False, nargs='?', default=True,
                       help='disable calculating maximum value(s)')
    parse.add_argument('--disable-row-count', type=bool, const=False, nargs='?', default=True,
                       help='disable calculating total row count')
    parse.add_argument('--where-conditions', type=str, default=None, help='User defined where conditions')
    parse.add_argument('--order-by', type=bool, default=False, const=True, nargs='?', help='whether to enable order by (min / max) timestamp')
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

    # increments query
    sql_query = query_data.build_increments_query(table_name=args.table_name, time_interval=args.interval,
                                                  time_column=args.time_column, units=args.time_units,
                                                  value_columns=values, calc_min=args.disable_calc_min,
                                                  calc_avg=args.disable_calc_avg, calc_max=args.disable_calc_max,
                                                  row_count=args.disable_row_count, where_condition=args.where_conditions,
                                                  order_by=args.order_by, limit=args.limit)

    output = query_data.query_data(conn=anylog_conn, db_name=args.db_name, sql_query=sql_query, output_format=args.output_format,
                                   stat=args.stat, timezone=args.timezone, include=args.include, extend=args.extend,
                                   view_help=args.view_help, return_cmd=args.return_cmd, exception=args.exception)

    if output['command'] is not None and args.view_help is False:
        print(output['command'], "\n")
    if output['results'] is not None:
        print(output['results'])


if __name__ == '__main__':
    main()