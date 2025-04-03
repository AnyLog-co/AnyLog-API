import datetime
import json
import random
import asyncio

import anylog_api.async_anylog_connector as anylog_connector

# Connect to AnyLog / EdgeLake connector
conn = '66.228.59.163:32349'
auth = ()
timeout = 30
anylog_conn = anylog_connector.AnyLogConnector(conn=conn, auth=auth, timeout=timeout)

async def main():
    if await anylog_connector.check_status(anylog_conn=anylog_conn) is True: # validate able to communicate with the node
        # validate node
        output = await anylog_connector.check_node(anylog_conn=anylog_conn)
        print(output)

        # validate communication with all nodes
        output = await anylog_connector.check_network(anylog_conn=anylog_conn)
        print(output)

        # view running processes
        output = await anylog_connector.get_processes(anylog_conn=anylog_conn)
        print(output)

        # Query data
        sql_cmd = "sql nov format=table select * from rand_data"
        output = await anylog_conn.get(command=sql_cmd, destination='network')
        print(output)

        sql_cmd = "sql nov format=json and stat=false select timestamp, value from rand_data where period(minute, 1, now(), timestamp)"
        output = await anylog_conn.get(command=sql_cmd, destination='network')
        output = json.loads(output)
        print(json.dumps(output, indent=2))


# Run the async main function
asyncio.run(main())
