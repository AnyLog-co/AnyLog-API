# AnyLog API 

The AnyLog API enables seamless interaction with _AnyLog_ or _EdgeLake_ nodes to manage distributed data seamlessly. 
This README provides setup instructions and sample usage for initializing a node, inserting data, and querying data.

## Requirements
* Python Installation: Python 3.7 or newer
* Library Installation: Install the AnyLog API library via pip
```shell
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade anylog-api>=0.0
```
* A running (generic) AnyLog or EdgeLake node
```shell
docker run -it -d --network host \
  -e INIT_TYPE=prod \
  -e NODE_TYPE=generic \
  -e ANYLOG_SERVER_PORT=32048 \
  -e ANYLOG_REST_PORT=32049 \
--name anylog-node --rm anylogco/anylog-network:latest  
```

## Support Links
* [AnyLog Documentation](https://github.com/AnyLog-co/documentation/)
* [EdgeLake Documentation](https://edgelake.github.io/)
* [AnyLog's docker-compose](https://github.com/AnyLog-co/docker-compose)
* [EdgeLake's docker-compose](https://github.com/EdgeLake/docker-compose)

## Usage Examples

### Node Initiation  
Code in [example_node_deployment](example_node_deployment), demonstrates deploying a node completely via REST based on
`.env` [configuration file](configs). 

**Key Features**: 
* Set up an AnyLog node or EdgeLake instance.
* Apply configurations, set license keys, and validate the node’s connectivity. 
* Schedule tasks, create databases, and establish blockchain synchronization.

```shell
python3 node.py <node_connection> --configs=<config_file> --license-key=<license_key> --edgelake
```

### Data Management
* Insert Data via PUT: 
```python
import datetime
import random 
import anylog_api.anylog_connector as anylog_connector
import anylog_api.data.publish_data as publish_data

# Generate data
SAMPLE_DATA = [] 
for i in range(10):
    SAMPLE_DATA.append({
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
        "value": random.random()
    })

# connect to AnyLog / EdgeLake
conn = '10.10.1.15:32149'
anylog_conn = anylog_connector.AnyLogConnector(conn=conn, timeout=30)

# Publish data
publish_data.put_data(conn=anylog_conn, payload=SAMPLE_DATA, db_name="test", table_name="rand_data",
                             mode='streaming', return_cmd=False, exception=True)
```
* Insert Data via POST: 
```python
import datetime
import random 
import anylog_api.anylog_connector as anylog_connector
import anylog_api.data.publish_data as publish_data

# Generate data
SAMPLE_DATA = [] 
for i in range(10):
    SAMPLE_DATA.append({
        "dbms": "test", 
        "table": "rand_data",
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
        "value": random.random()
    })


conn = '10.10.1.15:32149'
topic = 'my-data'

# connect to AnyLog / EdgeLake
anylog_conn = anylog_connector.AnyLogConnector(conn=conn, timeout=30) 

# create message client
publish_data.run_msg_client(conn=anylog_conn, broker='rest', topic=topic, db_name="bring [dbms]",
                                table_name="bring [table]",
                                values={
                                    "timestamp": {"type": "timestamp", "value": "bring [timestamp]"},
                                    "value": {"type": "float", "value": "bring [value]"}
                                }, destination="", is_rest_broker=True, view_help=False, return_cmd=False, exception=True)

# Publish data
publish_data.post_data(conn=anylog_conn, payload=SAMPLE_DATA, topic=topic, return_cmd=False, exception=True)
```
* Query Data

```python
import anylog_api.anylog_connector as anylog_connector
import anylog_api.data.query as query_data

conn = '10.10.1.15:32349'
anylog_conn = anylog_connector.AnyLogConnector(conn=conn, timeout=30)

sql_cmd = "SELECT COUNT(*) FROM rand_data"
output = query_data.query_data(conn=anylog_conn, db_name='test', sql_query=sql_cmd, output_format='table')
print(output)
```

