import datetime
import json
import random
import asyncio

import anylog_api.async_anylog_connector as anylog_connector

# Connect to AnyLog / EdgeLake connector
conn = '173.255.196.108:32149'
auth = ()
timeout = 30
anylog_conn = anylog_connector.AnyLogConnector(conn=conn, auth=auth, timeout=timeout)

async def main():
    # Connect to AnyLog / EdgeLake connector
    conn = '170.187.157.30:32149'
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

    if await anylog_connector.check_status(anylog_conn=anylog_conn) is True: # validate able to communicate with the node
        # prepare msg client
        await anylog_conn.post(command=command, topic=None, destination=None, payload=None) # publish message client
        msg_client = await anylog_conn.get(command='get msg client', destination=None)
        print(msg_client)

        # publish data
        status = await anylog_conn.post(command='data', topic='dummy-anylog', destination=None, payload=SERIALIZED_DATA)
        print('success' if status is True else 'fail')

        # validate data has been published
        msg_client = await anylog_conn.get(command='get msg client', destination=None)
        print(msg_client)

        # show streaming
        output = await anylog_conn.get(command='get streaming')
        print(output)

# Run the async main function
asyncio.run(main())


