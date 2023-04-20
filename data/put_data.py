import argparse
import datetime
import random
import uuid

import anylog_connector
import support
import data_management

DATA = [
    {
        "id": str(uuid.uuid4()),
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'value': random.random(),
        'unit': 'Celsius'
    },
    {
        "id": str(uuid.uuid4()),
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'value': random.random(),
        'unit': 'Celsius'
    },
    {
        "id": str(uuid.uuid4()),
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'value': random.random(),
        'unit': 'Celsius'
    }
]




def main():
    """
    The following provides an example of POST-ing data into AnyLog
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#using-a-put-command
    :process:
        1. declare MQTT client if not declared
            <run mqtt client where broker=rest and port=2049 and user-agent=anylog and log=false and topic=(
                name=new-topic and
                dbms=test and
                table=test and
                column.id=(type=str and value="bring [id]") and
                column.timestamp.timestamp="bring [timestamp]" and
                column.value=(type=float and value="bring [value]") and
                column.unit=(type=str and value="bring unit")
            )>
        2. Prepare data (serialize)
        3. POST data
    :positional arguments:
        rest_conn             REST connection information
    :optional arguments:
        -h, --help                      show this help message and exit
        --db-name       DB_NAME         logical database to store data in (default: test)
        --table-name    TABLE_NAME      table to store data in (default: test)
        --timeout       TIMEOUT         REST timeout (default: 30)
        --mode          MODE            format to ingest data (default: streaming)
            file - The body of the message is JSON data. Database load (on an Operator Node) and data send
                   (on a Publisher Node) are with no wait. File mode is the default behaviour.
            streaming - The body of the message is JSON data that is buffered in the node. Database load
                        (on an Operator Node) and data send (on a Publisher Node) are based on time and volume
                        thresholds.
        -e,--exception  [EXCEPTION]     Whether to print errors (default: False)
    :global:
        DATA:list - list of values to publish against the node
    :params:
        headers:dict - REST header information
        conn:str - REST connection IP:Port
        auth:tuple - authentication information for REST
        anylog_conn:anylog_connector.AnyLogConnector - AnyLog connection
        json_string:str - JSON string of Data
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn', type=support.validate_conn_pattern, default='127.0.0.1:2049', help='REST connection information')
    parser.add_argument("--db-name", type=str, default="test", help="logical database to store data in")
    parser.add_argument("--table-name", type=str, default="sample_data", help="table to store data in")
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument("--mode", type=str, choices=["streaming", "file"], default="streaming", help="format to ingest data")
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = parser.parse_args()

    conn, auth = support.anylog_connection(rest_conn=args.rest_conn)
    anylog_conn = anylog_connector.AnyLogConnector(conn=conn, auth=auth, timeout=args.timeout, exception=args.exception)

    json_string = support.serialize_row(data=DATA)
    if data_management.put_data(anylog_conn=anylog_conn, payload=json_string, db_name=args.db_name,
                                table_name=args.table_name, mode=args.mode) is False:
        print(f"Failed to publish data against {conn} via PUT")


if __name__ == '__main__':
    main()