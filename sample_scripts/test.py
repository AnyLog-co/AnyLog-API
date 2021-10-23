"""
The following is intend to try specific methods within the API code
"""
import __init__
import anylog_api
import get_cmd

rest_conn='45.33.41.185:2049'
master_node='45.33.41.185:2048'
auth=None
timeout=30

# connect to AnyLog
anylog_conn = anylog_api.AnyLogConnect(conn=rest_conn, auth=auth, timeout=timeout)
print(get_cmd.get_authentication(conn=anylog_conn, exception=True))