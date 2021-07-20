# AnyLog Init Scripts 

The following scripts are intended specific node(s). 

**Command**: 

```python3 AnyLog-Network/source/cmd/user_cmd.py process AnyLog-Network/anylog_deployment_scripts/${node_type}_init.al``` 

## Node process
A node is initated in the following manner:

   0. AnyLog starts as a docker (alpine or debian) or locally via [run_anylog.sh](../run_anylog.sh)
   1. Declare the root dir for AnyLog
   2. Declare params - [declare_params.al](declare_params.al)
   3. Connect to TCP and REST ports
   4. Connect to database(s)
   5. Declare to blockchain - blockchain decloration 
      * Policy Type
      * hostname 
      * policy node name 
      * company 
      * IPs and Ports 
      * location - if fails to locate machine via [ipinfo](https://ipinfo.io/json) use "0.0, 0.0"
      * For Operator
      * --> physical databaase type  
      * --> logicla database name 
      ```
      {"operator" : {
          "hostname": !hostname,
          "name": !node_name,
          "company": !company_name,
          "local ip" : !ip,
          "ip": !external_ip,
          "port" : !anylog_server_port,
          "rest_port": !anylog_rest_port,
          "db type": !db_type,
          "dbms": !default_dbms,
          "loc": !loc
        }
      }
      ```
   6. If **Operator**  - set partition(s) and run operator

      If **Publisher** - run publisher

      If **Master** of **Query** skip to Step 7
   7. Run blockchain sych

## Run Files 
```
/home/anylog/AnyLog-Network/anylog_deployment_scripts/
├── declare_params.al       <-- Declare parameters for specific node
├── blockchain_pull_json.al <-- Copy blockchain to node
├── declare_device.al       <-- declare specific device (non-node) to blockchain
├
├── master_init.al          <-- Init master node
├──── declare_master.al     <-- declare node on blockchain
├
├── operator_init.al        <-- Init operator node
├──── declare_operator.al   <-- declare node on blockchain
├
├── publisher_init.al      <-- Init publisher node
├──── declare_publisher.al <-- declare node on blockchain
├
├── query_init.al          <-- Init query node
├──── declare_query.al     <-- declare node on blockchain
├
├── drop_policy.al         <-- Based on $NODE_TYPE, name and company drop policy. If $NODE_TYPE is operator then call drop_cluster.al 
└── drop_cluster.al        <-- Check whether there exists correlated operators, if not, drops cluster (runs sas part fo drop_policy) 

* Disclaimer - the drop policy must occur on the correlated node 
```
