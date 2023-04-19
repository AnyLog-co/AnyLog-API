import argparse
import pytz

import deployment_support

import anylog_connector
import data_management

TIMEZONES = list(pytz.all_timezones_set)
TIMEZONES.append('local')


def main():
    """
    :positional arguments:
        rest_conn             REST connection information
    :optional arguments:
        -h, --help                      show this help message and exit
        --db-name       DB_NAME         logical database to store data in (default: test)
        --table-name    TABLE_NAME      table to store data in (default: sample_data)
        --timeout       TIMEOUT         REST timeout (default: 30)
        --format        FORMAT          The format of the result set (default: json)
        --timezone      TIMEZONE        used for time values in the result set (default: local)
        --include       INCLUDE         Allows to treat remote tables with a different name as the table being queried (default: None)
        --extend        EXTEND          Include node variables (which are not in the table data) in the query result set. (default: None)
        --stat          [STAT]          Adds processing statistics to the query output (default: False)
        --dest          DEST            Destination of the query result set (default: None)
        --file-name     FILE_NAME       File name for the output data (default: None)
        --table         TABLE           A table name for the output data (default: None)
        --test          [TEST]          The output is organized as a test output (default: False)
        --source        SOURCE          A file name that is used in a test process to determine the processing result (default: None)
        --title         TITLE           Added to the test information in the test header (default: None)
        --destination   DESTINATION     where to query against (default: network)
    :params:
        conn:str - REST connection IP:Port
        auth:tuple - authentication information for REST
        anylog_conn:anylog_connector.AnyLogConnector - AnyLog connection
        output:str - results
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn', type=deployment_support.validate_conn_pattern, default='127.0.0.1:2049',
                        help='REST connection information')
    parser.add_argument("--db-name", type=str, default="test", help="logical database to store data in")
    parser.add_argument("--table-name", type=str, default="sample_data", help="table to store data in")
    parser.add_argument("--timeout", type=int, default=30, help='REST timeout')
    parser.add_argument("--format", type=str, default='json', choices=['json', 'table'], help='The format of the result set')
    parser.add_argument("--timezone", type=str, default='local', choices=TIMEZONES, help='Timezone used for time values in the result set')
    parser.add_argument("--include", type=str, default=None, help='Allows to treat remote tables with a different name as the table being queried')
    parser.add_argument("--extend", type=str, default=None, help='Include node variables (which are not in the table data) in the query result set.')
    parser.add_argument("--stat", type=bool, nargs='?', default=False, const=True, help='Adds processing statistics to the query output')
    parser.add_argument("--dest", type=str, default=None, choices=[None, "stdout", "rest", "dbms", "file"], help="Destination of the query result set")
    parser.add_argument("--file-name", type=str, default=None, help='File name for the output data')
    parser.add_argument("--table", type=str, default=None, help='A table name for the output data')
    parser.add_argument("--test", type=bool, nargs='?', default=False, const=True, help='The output is organized as a test output')
    parser.add_argument("--source", type=str, default=None, help="A file name that is used in a test process to determine the processing result")
    parser.add_argument("--title", type=str, default=None, help="Added to the test information in the test header")
    parser.add_argument("--destination", type=str, default="network", help="where to query against")
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False,
                        help='Whether to print errors')
    args = parser.parse_args()

    conn, auth = deployment_support.anylog_connection(rest_conn=args.rest_conn)
    anylog_conn = anylog_connector.AnyLogConnector(conn=conn, auth=auth, timeout=args.timeout, exception=args.exception)

    for sql_query in [
        f"SELECT COUNT(*) FROM {args.table_name}",
        f"SELECT increments(minute, 1, timestamp), MIN(timestamp), MAX(timestamp), MIN(value), AVG(value), MAX(value) FROM {args.table_name} WHERE timestamp <= NOW()",
        f"SELECT MIN(timestamp), MAX(timestamp), MIN(value), AVG(value), MAX(value) FROM {args.table_name} WHERE period(minute, 1, NOW(), timestamp)"
    ]:

        output = data_management.query_data(anylog_conn=anylog_conn, db_name=args.db_name, sql_query=sql_query,
                                            format=args.format, timezone=args.timezone, include=args.include,
                                            extend=args.extend, stat=args.stat, dest=args.dest, file_name=args.file_name,
                                            table=args.table, test=args.test, source=args.source, title=args.title,
                                            destination=args.destination, view_help=False)
        print(f"Query: {sql_query}")
        print(output)


if __name__ == '__main__':
    main()