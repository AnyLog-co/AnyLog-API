# AnyLog API 

## File Struct
**Base**:
* [anylog_api.py](anylog_api/anylog_api.py) -- this is the "main" that users import 
* [anylog_rest_api.py](anylog_api/anylog_rest_api.py) -- REST connection and communication code 
* [list_cmds.py](anylog_api/list_cmds.py) <-- support to get information about functions

**AnyLog Commands**:
* [status.py](backup/status.py) 
  * node status
  * test node
  * test network 
* [logging.py](backup/logging.py)  
  * event log
  * error log
  * echo queue 
* [processes.py](backup/processes.py) 
  * get processes
  * run operator
  * get operator
  * run publisher 
  * get publisher 
* southbound 
  * run msg client
  * get msg client
  * plc related (future)
* blockchain
  * create policy 
  * declare policy 
  * drop policy 
  * get policy 
  * blockchain sync
* scheduler 
  * get scheduler 
  * run scheduler 
  * add task 
  * run scheduled pull
* data 
  * add data via PUT 
  * add data via POST 
  * query builder (post increments / period)
  * execute query
* dbms
  * connect database 
  * get databases
  * run archiver 
  