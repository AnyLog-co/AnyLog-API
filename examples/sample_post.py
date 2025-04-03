import datetime
import json
import random

import anylog_api.anylog_connector as anylog_connector

# Connect to AnyLog / EdgeLake connector
conn = '173.255.196.108:32149'
auth = ()
timeout = 30
anylog_conn = anylog_connector.AnyLogConnector(conn=conn, auth=auth, timeout=timeout)

# Generate and serialize data
DATA = []
for i in range(10):
    DATA.append({
        'dbms': 'nov',
        'table': 'rand_data',
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
        "value": random.random()
    })

SERIALIZED_DATA = json.dumps(DATA)

# create message client
command = 'run msg client where broker=rest and user-agent=anylog and log=false and topic=(name=dummy-anylog and dbms="bring [dbms]" and table="bring [table]" and column.timestamp.timestamp="bring [timestamp]" and column.value.float="bring [value]")'

if anylog_connector.check_status(anylog_conn=anylog_conn) is True: # validate able to communicate with the node
    # prepare msg client
    anylog_conn.post(command=command, topic=None, destination=None, payload=None) # publish message client
    msg_client = anylog_conn.get(command='get msg client', destination=None)
    print(msg_client)

    # publish data
    status = anylog_conn.post(command='data', topic='dummy-anylog', destination=None, payload=SERIALIZED_DATA)
    print('success' if status is True else 'fail')

    # validate data has been published
    msg_client = anylog_conn.get(command='get msg client', destination=None)
    print(msg_client)
    # show streaming
    output = anylog_conn.get(command='get streaming')
    print(output)




