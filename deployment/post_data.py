import argparse
import datetime
import json
import random
import uuid

import deployment_support

import anylog_connector
import generic_get
import generic_post

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


def serialize_row(data:dict):
    try:
        return json.dumps(data)
    except Exception as error:
        print(f"Failed to serialize data")


def main():
    """
    The following provides an example of POST-ing data into AnyLog
    :process:
        1. declare MQTT client
            <run mqtt client where broker=rest and port=2049 and user-agent=anylog and log=false and topic=(
                name=new-topic and
                dbms=test and
                table=test and
                column.id=(type=str and value="bring [id]") and
                column.timestamp.timestamp="bring [timestamp]" and
                column.value=(type=float and value="bring [value]") and
                column.unit=(type=str and value="bring unit")
            )>
        2. Prepare data
        3. POST data
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn', type=deployment_support.validate_conn_pattern, default='127.0.0.1:2049',
                        help='REST connection information')
    parser.add_argument("--topic-name", type=str, default="new-topic", help="Topic name")
    parser.add_argument("--db-name", type=str, default="test", help="logical database to store data in")
    parser.add_argument("--table-name", type=str, default="test", help="table to store data in")
    parser.add_argument("--mqtt-configs", type=str, default='rest:2049', help="MQTT connection configuration")
    parser.add_argument("--enable-log", type=bool, nargs='?', const=True, default=False, help="enable MQTT logs")
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = parser.parse_args()

    conn, auth = deployment_support.anylog_connection(rest_conn=args.rest_conn)
    anylog_conn = anylog_connector.AnyLogConnector(conn=conn, auth=auth, timeout=args.timeout, exception=args.exception)
    broker, auth = deployment_support.anylog_connection(rest_conn=args.mqtt_configs)
    broker_ip, broker_port = broker.split(":")
    user = None
    password = None
    if auth is not None:
        user, password = auth

    mqtt_params = {
        "id": {
            "type": "str",
            "value": "bring [id]"
        },
        "timestamp": {
            "type": "timestamp", # for current timestamp users can just state "NOW()"
            "value": "bring [timestamp]"
        },
        "value": {
            "type": "float",
            "value": "bring [value]"
        },
        "unit": {
            "type": "str",
            "value": "bring unit"
        }
    }

    if broker_ip in ["rest", "local"]:
        mqtt_client = generic_get.get_msg_client(anylog_conn=anylog_conn, topic=args.topic_name, broker=broker_ip,
                                                 id=None, view_help=False)
    else:
        mqtt_client = generic_get.get_msg_client(anylog_conn=anylog_conn, topic=args.topic_name, broker=broker,
                                                 id=None, view_help=False)

    if mqtt_client == "No such client subscription":
        if generic_post.run_mqtt_client(anylog_conn=anylog_conn, broker=broker_ip, port=broker_port, user=user, password=password,
                                        log=args.enable_log, topic_name=args.topic_name, db_name=args.db_name,
                                        table_name=args.table_name, params=mqtt_params, view_help=False) is False:
            print(f"Failed to declare MQTT client process against {conn}")

    json_string = serialize_row(data=DATA)
    if generic_post.publish_data(anylog_conn=anylog_conn, topic=args.topic_name, payload=json_string) is False:
        print(f"Failed to publish data against {conn}")


if __name__ == '__main__':
    main()


