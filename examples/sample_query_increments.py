import argparse
import anylog_api.anylog_connector as anylog_connector
import anylog_api.generic.get as generic_get
import anylog_api.data.query as query_data
import __support__ as support


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("conn", type=support.check_conn, default="127.0.0.1:32149",
                       help="Connection information to send data into AnyLog/EdgeLake")
    parse.add_argument("--db-name", type=str, default="test", help="logical database name")
    parse.add_argument("--table-name", type=str, default="sample_data", help="physical table name")
    parse.add_argument('--exception', type=bool, default=False, const=True, nargs='?',
                       help="Whether to print exceptions")
    args = parse.parse_args()

    conn = list(args.conn)[0]
    anylog_conn = anylog_connector.AnyLogConnector(conn=conn, timeout=30)
    node_status = generic_get.get_status(conn=anylog_conn, view_help=False, return_cmd=False, exception=args.exception)
    if node_status is False:
        raise f"Failed to communicate with node against {args.conn}. Cannot continue..."

    # increments query
    increments_query = query_data.build_increments_query(table_name=args.table_name, time_interval='minute', units=5,
                                                         date_column='timestamp', other_columns={'value': 'float'},
                                                         ts_min=True, ts_max=True, row_count=True,
                                                         where_condition='timestamp >= NOW() - 1 hour',
                                                         order_by='asc', limit=10, exception=args.exception)

    print(f"Query: {increments_query}")
    print(query_data.query_data(conn=anylog_conn, db_name=args.db_name, sql_query=increments_query,
                                output_format='table', destination='network', return_cmd=False,
                                exception=args.exception))


    increments_query = query_data.build_increments_query(table_name=args.table_name, time_interval='minute', units=5,
                                                         date_column='timestamp', other_columns={'value': ['min', 'max', 'avg', 'sum']},
                                                         ts_min=True, ts_max=True, row_count=False,
                                                         where_condition='timestamp >= NOW() - 1 hour',
                                                         order_by='asc', limit=10, exception=args.exception)

    print(f"Query: {increments_query}")
    print(query_data.query_data(conn=anylog_conn, db_name=args.db_name, sql_query=increments_query,
                                output_format='table', destination='network', return_cmd=False,
                                exception=args.exception))

    increments_query = query_data.build_increments_query(table_name=args.table_name, time_interval='minute', units=5,
                                                         date_column='timestamp',
                                                         other_columns=['min(value)::int', 'avg(value)::float(3)', 'max(value)::int'],
                                                         ts_min=True, ts_max=True, row_count=False,
                                                         where_condition='timestamp >= NOW() - 1 hour',
                                                         order_by='asc', limit=10, exception=args.exception)

    print(f"Query: {increments_query}")
    print(query_data.query_data(conn=anylog_conn, db_name=args.db_name, sql_query=increments_query,
                                output_format='table', destination='network', return_cmd=False,
                                exception=args.exception))


if __name__ == '__main__':
    main()