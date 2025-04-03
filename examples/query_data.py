import json
import anylog_api.anylog_connector as anylog_connector

# Connect to AnyLog / EdgeLake connector
conn = '127.0.0.1:32349'
auth = ()
timeout = 30
anylog_conn = anylog_connector.AnyLogConnector(conn=conn, auth=auth, timeout=timeout)

if anylog_connector.check_status(anylog_conn=anylog_conn) is True: # validate able to communicate with the node
    # validate node
    output = anylog_connector.check_node(anylog_conn=anylog_conn)
    print(output)

    # validate communication with all nodes
    output = anylog_connector.check_network(anylog_conn=anylog_conn)
    print(output)

    # view running processes
    output = anylog_connector.get_processes(anylog_conn=anylog_conn)
    print(output)

    # Query data
    sql_cmd = "sql test format=table select * from rand_data"
    output = anylog_conn.get(command=sql_cmd, destination='network')
    print(output)

    sql_cmd = "sql test format=json and stat=false select timestamp, value from rand_data where period(minute, 1, now(), timestamp)"
    output = anylog_conn.get(command=sql_cmd, destination='network')
    print(json.dumps(output, indent=2))
