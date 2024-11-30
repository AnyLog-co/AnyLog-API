import argparse
import random

from anylog_api.anylog_api import AnyLogAPI
import anylog_api.__support__ as anylog_api_support
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
    parse.add_argument("conn", type=anylog_api_support.validate_conn_info, default="127.0.0.1:32149",
                       help="Connection information to send data into AnyLog/EdgeLake")
    parse.add_argument("--db-name", type=str, default="test", help="logical database name")
    parse.add_argument("--table-name", type=str, default="sample_data", help="physical table name")
    parse.add_argument("--total-rows", type=int, default=10, help="number of rows to generate")
    parse.add_argument("--wait-time", type=float, default=0.5, help="How long to wait between each row")
    parse.add_argument("--topic", type=str, default='sample-topic', help='REST topic name')
    parse.add_argument("--timeout", type=float, default=30, help="REST request timeout")
    parse.add_argument('--exception', type=bool, default=False, const=True, nargs='?',
                       help="Whether to raise / print exceptions")
    args = parse.parse_args()


    # validate node is accessible
    for conn in args.conn:
        args.conn[conn] = AnyLogAPI(conn=conn, timeout=args.timeout, exception=args.exceptions)
        node_status = args.conn[conn].get_status(destination=None, view_help=False)
        if node_status is False:
            raise ConnectionError(f'Failed to connect to node against {conn}')

    # declare message client
    message_client = (f'run msg client where broker=rest and user-agent=anylog and log=false and topic=(' +
                      f'name={args.topics} and dbms={args.db_name} and table={args.table_name} and '
                      f'column.timestamp.timestamp=now() and column.value=(type=float and value="bring [value]"))')

    for conn in args.conn:
        if not args.conn[conn].execute_post(command=message_client, payload=None, topic=None, destination=None, view_help=False):
            raise ConnectionError(f'Failed to declare Message Client against {conn}')

    # Generate rows - notice db_name and table are specified in the data generator
    payloads = support.data_generator(db_name=args.db_name, table=args.table_name, total_rows=args.total_rows,
                                      wait_time=args.wait_time)

    # publish data into AnyLog / EdgeLake
    if len(list(args.conn.keys())) == 1:
        args.conn[list(args.conn.keys())[0]].execute_post(command='data', payload=payloads, topic=args.topic,
                                                          destination=None, view_help=False)
    else:
        last_conn = None
        conn = random.choice(list(args.conn.keys()))
        for payload in payloads:
            while last_conn == conn:
                conn = random.choice(list(args.conn.keys()))
            args.conn[conn].execute_post(command='data', payload=payload, topic=args.topic, destination=None,
                                         view_help=False)
            last_conn = conn

if __name__ == '__main__':
    main()
