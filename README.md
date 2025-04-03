# AnyLog API 

The AnyLog API enables seamless interaction with _AnyLog_ or _EdgeLake_ nodes to manage distributed data seamlessly. 
This README provides setup instructions and sample usage for initializing a node, inserting data, and querying data.


pip install anylog-api 
import anylog_api.anylog_conneector || anylo[async_anylog_connector.py](anylog_api/async_anylog_connector.py)

anylog_conn = AnyLogConnector(conn='127.0.0.1:32')
anylog_conn.get(cmd, dest=None)

