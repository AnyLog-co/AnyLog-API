# AnyLog API 

The following provides the source code for a pip package that allows to easily communicate with AnyLog / EdgeLake via 
REST.

A full list of functions can be found [here](FUNCTIONS.md).  

## Sample Code 
The following provides samples calls demonstrating to communicate with the API.
```python3 
from anylog_api.anylog_api import AnyLogAPI


anylog_conn = AnyLogAPI(conn="http://23.239.12.151:32349")

print(anylog_conn.__help__()) # list functions and what they do 

print(anylog_conn.exec_mode) # list execution mode 
print(anylog_conn.node_status.get_status()) # return node status 

anylog_conn.update_exec_mode(exec_mode="command") # set execution mode 
print(anylog_conn.node_status.get_status(json_frmt=True)) # return generated command

anylog_conn.update_exec_mode(exec_mode="help") # set execution mode
anylog_conn.node_status.get_status(json_frmt=True) #  return `help` for `get status`
```

**todo / Examples list**:
1. every command should either <-- I believe that exists but missing `return` for non-GET 
   * execute - exists 
   * return help 
   * return command rather than execute 
2. sample for deployment-scripts via REST
3. Sample for deployment-scripts via Policy
4. sample for aggregation example