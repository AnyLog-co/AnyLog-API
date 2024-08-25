import argparse
import anylog_api.anylog_connector as anylog_connector
import anylog_api.generic.get as generic_get
import anylog_api.data.publish_data as publish_data
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
        --topic         TOPIC           REST topic name
        --wait-time     WAIT_TIME       How long to wait between each row
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
    parse.add_argument("--topic", type=str, default='sample-topic', help='REST topic name')
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

    publish_data.run_msg_client(conn=anylog_conn, broker='rest', topic=args.topic, db_name="bring [dbms]",
                                table_name="bring [table]",
                                values={
                                    "timestamp": {"type": "timestamp", "value": "bring [timestamp]"},
                                    "value": {"type": "float", "value": "bring [value]"}
                                }, destination="", is_rest_broker=True, view_help=False, return_cmd=False, exception=args.exception)


    # Generate rows - notice db_name and table are specified in the data generator
    payloads = support.data_generator(db_name=args.db_name, table=args.table_name, total_rows=args.total_rows,
                                      wait_time=args.wait_time)

    status = True
    for row in payloads:
        if publish_data.post_data(conn=anylog_conn, payload=row, topic=args.topic, return_cmd=False,
                                  exception=args.exception) is False:
            status = False

    if status is False:
        print("Successfully inserted data")
    else:
        print("Successfully inserted data")




if __name__ == '__main__':
    main()
