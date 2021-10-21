import __init__
from adding_data import post_data
import anylog_api

import argparse
from data_generator import data_generator


def main():
    """
    The following provides an example of how to POST data into AnyLog
    :requirement:
        User should have an MQTT client running on the node using REST broker type
    :positional arguments:
        rest_conn             REST connection information
        mqtt_topic            MQTT topic for REST
        db_name               logical database to send data into
        table_name            table within logical database to store data in
    :optional arguments:
        -h, --help                  show this help message and exit
        -a, --auth      AUTH        REST authentication information     (default: None)
        -t, --timeout   TIMEOUT     REST timeout period                 (default: 30)
    :params:
        anylog_conn:anylog_api.AnyLogConnect - connection to AnyLog
        data:dict - data generated using data_generator.put_data_generator
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn',  type=str, default='127.0.0.1:2049',  help='REST connection information')
    parser.add_argument('mqtt_topic', type=str, default='mqtt-rest',       help='MQTT topic for REST')
    parser.add_argument('db_name',    type=str, default='sample_database', help='logical database to send data into')
    parser.add_argument('table_name', type=str, default='sample_table',    help='table within logical database to store data in')
    parser.add_argument('-a', '--auth',    type=tuple, default=None, help='REST authentication information')
    parser.add_argument('-t', '--timeout', type=int,   default=30,   help='REST timeout period')
    args = parser.parse_args()

    anylog_conn = anylog_api.AnyLogConnect(conn=args.rest_conn, auth=args.auth, timeout=args.timeout)
    data = data_generator(db_name=args.db_name, table_name=args.table_name)
    if not post_data(conn=anylog_conn, rest_topic=args.mqtt_topic, data=data, exception=True):
        print('Failed to POST data into AnyLog')


if __name__ == '__main__':
    main()