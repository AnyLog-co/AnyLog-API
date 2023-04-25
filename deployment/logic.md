**Required**: 
0. network configuration policy - this step should be by the node during deployment
   * logic for TCP
```commandline
if bind is True:
    new_policy[!policy_type][ip] = !external_ip
    new_policy [!policy_type][local_ip] = !ip
elif bind is False: 
    new_policy[!policy_type][ip] = !ip
```
   * logic from REST
```commandline
pass
```
  * logic for broker
```commandline
pass
```
1. `set license key`  

2. 
   * cluster - if operator node
   * node policy for master / operator / query / publisher
```commandline
if bind is True:
    new_policy[!policy_type][ip] = !external_ip
    new_policy [!policy_type][local_ip] = !ip
elif bind is False: 
    new_policy[!policy_type][ip] = !ip
```

3. if deploy based on configuration then a configuration policy - will include: 
   * `run scheduler 1`
   * `run blockchain sync`
   * `connect dbms`
     * blockchain for master 
     * default_dbms for operator 
     * almgm for operator + publisher 
     * system_query for query node or if configured
   * `create table` 
     * blockchain.ledger
     * almgm.tsd_info
   * if _operator_ node:
     * if valid - `connnect dbms` for MongoDB 
     * data partitioning
       * `partition !default_dbms`
       * `schedule` a drop process to remove old partitioned data  
     * if HA is enabled
       *  `run data distributor`
       * `run data consumer` 
       * `set consumer mode`
     * `run operator`
     * if set - `run mqtt client`
   * if _publisher_ node: 
     * `run publisher` 
     * if set - `run mqtt client`

4. if deploy by policy is **True** then execute config policy that contains step 3. However, deploy by policy is 
**False**, then each step within step 3 should be done already & there's no need for step 4. 
