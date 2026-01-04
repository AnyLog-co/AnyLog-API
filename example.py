from anylog_api.anylog_api import AnyLogAPI


anylog_conn = AnyLogAPI(conn="http://23.239.12.151:32349")
# print(anylog_conn.help())
# print(anylog_conn.node_status.get_status())
# print(anylog_conn.node_status.test_node())
# print(anylog_conn.node_status.test_network())
print(anylog_conn.logging.get_event_log())