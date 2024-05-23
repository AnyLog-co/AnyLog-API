import argparse
import anylog_api.anylog_connector as anylog_connector
import anylog_api.generic.get as generic_get
import anylog_api.data.publish_data as publish_data
import __support__ as support


def main():
    """
    Send data via PUT - REST
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
    parse.add_argument("--db-name", type=str, default="test", help="logical database name")
    parse.add_argument("--table-name", type=str, default="sample_data", help="physical table name")
    parse.add_argument("--total-rows", type=int, default=10, help="number of rows to generate")
    parse.add_argument("--wait-time", type=float, default=0.5, help="How long to wait between each row")
    parse.add_argument("--publish-mode", type=str, default='streaming', choices=['streaming', 'file'],
                       help='Publishing mode')
    parse.add_argument("--timeout", type=float, default=30, help="REST request timeout")
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

    # Generate rows - notice db_name and table are not specified in the data generator
    payloads = support.data_generator(db_name=None, table=None, total_rows=args.total_rows, wait_time=args.wait_time)

    if publish_data.put_data(conn=anylog_conn, payload=payloads, db_name=args.db_name, table_name=args.table_name,
                             mode='streaming', return_cmd=False, exception=args.exception) is True:
        print("Successfully inserted data")
    else:
        print(f"Failed to insert data into {anylog_conn.conn}")





if __name__ == '__main__':
    main()
