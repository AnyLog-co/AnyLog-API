import argparse
import datetime
import json
import anylog_api.anylog_connector as anylog_connector
import anylog_api.generic.get as generic_get
import anylog_api.data.query as query_data
import anylog_api.data.publish_data as publish_data
import __support__ as support

FORMAT_STR = "%Y-%m-%d %H:%M:%S.%f"


def __get_timestamps(conn:anylog_connector.AnyLogConnector, db_name:str, table_name:str, time_column:str='timestamp',
                     exception:bool=False):
    output = query_data.query_data(conn=conn, db_name=db_name,
                                   sql_query=f"select min({time_column}) as min_ts, max({time_column}) as max_ts from {table_name}",
                                   output_format='json:list', stat=False, timezone='utc', view_help=False,
                                   return_cmd=False, exception=exception)
    output = json.loads(output['results'].split("]")[0])
    return datetime.datetime.strptime(output['min_ts'], FORMAT_STR), datetime.datetime.strptime(output['max_ts'], FORMAT_STR)


def __get_data(conn:anylog_connector.AnyLogConnector, db_name:str, table_name:str, time_column:str='timestamp',
               min_ts:str=None, max_ts:str=None, exception:bool=False):
    data = []
    query = f"select * from {table_name} where {time_column} >= '{min_ts}' and {time_column} <= '{max_ts}'"
    output = query_data.query_data(conn=conn, db_name=db_name,
                                   sql_query=query,
                                   output_format='json', stat=False, timezone='utc', view_help=False,
                                   return_cmd=False, exception=exception)
    try:
        for row in output['results']['Query']:
            for key in ['row_id', 'insert_timestamp', 'tsd_name', 'tsd_id']:
                if time_column != key:
                    del row[key]
            data.append(row)
    except:
        pass
    return data

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('conn1', type=support.check_conn, default='127.0.0.1:32349', help='(Query) REST connection to get data from')
    parse.add_argument('conn2', type=support.check_conn, default='127.0.0.1:32149', help='(Operator) REST connection to get data from')
    parse.add_argument('--db-name', type=str, default='new_company', help='logical database name')
    parse.add_argument('--table', type=str, default='rand_data', help='physical table name')
    parse.add_argument('--time-column', type=str, default='insert_timestamp', help='Timestamp column for where condition')
    parse.add_argument("--timeout", type=float, default=30, help="REST request timeout")
    parse.add_argument('--exception', type=bool, default=False, const=True, nargs='?',
                       help="Whether to print exceptions")
    args = parse.parse_args()

    conn, auth = next(iter(args.conn1.items()))
    query_conn = anylog_connector.AnyLogConnector(conn, auth=auth, timeout=args.timeout)
    if generic_get.get_status(conn=query_conn, destination=None, view_help=False, return_cmd=False,
                              exception=args.exception) is False:
        print(f"Failed to communicated with {query_conn.conn}. cannot continue...")
        exit(1)
    conn, auth = next(iter(args.conn2.items()))
    operator_conn = anylog_connector.AnyLogConnector(conn, auth=auth, timeout=args.timeout)
    if generic_get.get_status(conn=query_conn, destination=None, view_help=False, return_cmd=False,
                              exception=args.exception) is False:
        print(f"Failed to communicated with {query_conn.conn}. cannot continue...")
        exit(1)

    min_ts, max_ts = __get_timestamps(conn=query_conn, db_name=args.db_name, table_name=args.table, time_column='timestamp', exception=args.exception)
    while min_ts <= max_ts:
        future_ts = min_ts + datetime.timedelta(hours=12)
        payloads = __get_data(conn=query_conn, db_name=args.db_name, table_name=args.table, time_column='timestamp', min_ts=min_ts,
                          max_ts=future_ts, exception=args.exception)
        if payloads:
            if publish_data.put_data(conn=operator_conn, payload=payloads, db_name=args.db_name, table_name=args.table,
                                     mode='streaming', return_cmd=False, exception=args.exception) is True:
                print("Successfully inserted data")
            else:
                print(f"Failed to insert data into {operator_conn.conn}")
        min_ts = future_ts


if __name__ == '__main__':
    main()
