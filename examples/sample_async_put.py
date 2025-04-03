import datetime
import json
import random
import asyncio

import anylog_api.async_anylog_connector as anylog_connector

async def main():
    # Connect to AnyLog / EdgeLake connector
    conn = '170.187.157.30:32149'
    auth = ()
    timeout = 30
    anylog_conn = anylog_connector.AnyLogConnector(conn=conn, auth=auth, timeout=timeout)

    # Generate and serialize data
    DATA = [{
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
        "value": random.random()
    } for _ in range(10)]

    SERIALIZED_DATA = json.dumps(DATA)

    # Validate communication with the node
    if await anylog_connector.check_status(anylog_conn):
        status = await anylog_conn.put(dbms='nov', table='rand_data', mode='streaming', payload=SERIALIZED_DATA)
        print('success' if status else 'fail')

    # Show streaming
    output = await anylog_conn.get(command='get streaming')
    print(output)


# Run the async main function
asyncio.run(main())
