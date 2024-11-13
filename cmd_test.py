import anylog_api.anylog_connector as anylog_connector
from anylog_api.anylog_connector_support import extract_get_results

headers = {'command': "get databases where format=json", 'User-Agent': 'AnyLog/1.23'}

conn=anylog_connector.AnyLogConnector(conn='45.79.74.39:32049')
output=extract_get_results(conn=conn, headers=headers)
print('blockchain' in output)
