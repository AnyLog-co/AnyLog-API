import argparse

import import_packages
import_packages.import_dirs()
from adding_data import mqtt_data
from data_generator import data_generator

def main():
    """
    The following provides an example of how to send data into AnyLog directly via MQTT
    :requirement:
        User should have an MQTT client running on the node
    :positional arguments:
        mqtt_conn             MQTT broker connection info. if using local broker, provide just the broker IP
        mqtt_port             MQTT connection port
        mqtt_topic            MQTT topic for REST
        db_name               logical database to send data into
        table_name            table within logical database to store data in
    :params:
        anylog_conn:anylog_api.AnyLogConnect - connection to AnyLog
        da  ta:dict - data generated using data_generator.put_data_generator
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('mqtt_conn',  type=str, default='[user]@[borker]:[passwd]', help='MQTT broker connection info. if using local broker, provide just the broker IP')
    parser.add_argument('mqtt_port',  type=int, default=2050, help='MQTT connection port')
    parser.add_argument('mqtt_topic', type=str, default='mqtt-rest',       help='MQTT topic for REST')
    parser.add_argument('db_name',    type=str, default='sample_database', help='logical database to send data into')
    parser.add_argument('table_name', type=str, default='sample_table',    help='table within logical database to store data in')
    args = parser.parse_args()

    data = data_generator(db_name=args.db_name, table_name=args.table_name)
    if not mqtt_data(mqtt_conn=args.mqtt_conn, mqtt_port=args.mqtt_port, mqtt_topic=args.mqtt_topic, data=data,
                     exception=True):
        print('Failed to send data into AnyLog via MQTT')


if __name__ == '__main__':
    main()