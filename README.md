# AnyLog API 

## File Struct

### Base
* [anylog_api.py](anylog_api/anylog_api.py) -- this is the "main" that users import
* [anylog_rest_api.py](anylog_api/anylog_rest_api.py) -- REST connection and communication code
* [list_cmds.py](anylog_api/support.py) -- support to get information about functions

---
### Functions

* [anylog_conn](anylog_api/anylog_rest_api.py) -- REST connection and communication code
  * help - Get list of commands  or information about a command
  * update_exec_mode - Update execution mode for a given command
* [node_status](anylog_api/api_node_status.py)
  * async_get_status - Execute `get status`
  * async_test_network - Test network status
  * async_test_node - Test node status
  * get_status - Execute `get status`
  * test_network - Test network status
  * test_node - Test node status
* [logging](anylog_api/api_logs.py)
  * async_disable_echo_queue - Disable echo queue
  * async_enable_echo_queue - Enable echo queue
  * async_get_echo_queue - Get echo queue
  * async_get_error_log - View error log
  * async_get_event_log - View event log
  * async_reset_echo_queue - Reset echo queue (size)
  * async_reset_error_log - Reset error log
  * async_reset_event_log - Reset event log
  * disable_echo_queue - Disable echo queue
  * enable_echo_queue - Enable echo queue
  * get_echo_queue - Get echo queue
  * get_error_log - View error log
  * get_event_log - View event log
  * reset_echo_queue - Reset echo queue (size)
  * reset_error_log - Reset event log
  * reset_event_log - Reset event log
* [processes](anylog_api/api_process.py)
  * async_get_operator - Get operator processing information
  * async_get_processes - Get status of anylog processes
  * async_get_publisher - Get publisher processing information
  * async_get_streaming - Get streaming
  * async_run_operator - Execute `run operator` to insert data
  * async_run_publisher - Execute `run publisher`
  * get_operator - Get operator processing information
  * get_processes - Get status of anylog processes
  * get_publisher - Get publisher processing information
  * get_streaming - Get streaming
  * run_operator - Execute `run operator` to insert data
  * run_publisher - Execute `run publisher`
* [blockchain](anylog_api/api_blockchain.py)
  * async_blockchain_get - Execute `blockchain get` against the blockchain
  * async_insert_policy - Insert blockchain policy
  * blockchain_get - Execute `blockchain get` against the blockchain
  * build_policy - Builder for blockchain policy
  * insert_policy - Insert blockchain policy


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