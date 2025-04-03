import datetime
import json
import random

import anylog_api.anylog_connector as anylog_connector

# Connect to AnyLog / EdgeLake connector
conn = '127.0.0.1:32149'
auth = ()
timeout = 30
anylog_conn = anylog_connector.AnyLogConnector(conn=conn, auth=auth, timeout=timeout)

# Generate and serialize data
DATA = []
for i in range(10):
    DATA.append({
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
        "value": random.random()
    })

SERIALIZED_DATA = json.dumps(DATA)

if anylog_connector.check_status(anylog_conn=anylog_conn) is True: # validate able to communicate with the node
    status = anylog_conn.put(dbms='test', table='rand_data', mode='streaming', payload=SERIALIZED_DATA) # publish data via PUT
    print('success' if status is True else 'fail')

# show streaming
output = anylog_conn.get(command='get streaming')
print(output)
