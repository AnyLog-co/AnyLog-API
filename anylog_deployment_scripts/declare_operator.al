#-------------------------------------------
# Add operator without cluster to blockchain
# 
# The general process 
#    1. Get location 
#    2. chekc if $TABLE is declared 
#    3. Based on table_status & external_ip process operator 
#       a) check if operator already exists 
#       b) set operator value if not exists 
#    4. declare operator in blockchain if set in step 3b 
#--------------------------------------------
# process !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_operator.al

# set debug off 
table_status = True 
if not $TABLE then table_status = False 


:declare-loc: 
on error goto declare-loc-error
if not !loc then 
do info = rest get where url = https://ipinfo.io/json
do if !info then loc = from !info bring [loc]
do else loc = "0.0, 0.0"
do if not !loc then loc = "0.0, 0.0"

:declare-operator: 
# no table | enable external ip 
if !table == "" and !member_id == "" then policy = {"operator" : {
    "hostname": !hostname, 
    "name": !node_name,
    "company": !company_name, 
    "local_ip" : !ip,
    "ip": !external_ip, 
    "port" : !anylog_server_port.int, 
    "rest_port": !anylog_rest_port.int, 
    "db type": !db_type,
    "dbms": !default_dbms, 
    "loc": !loc
   }
}
else if !table == "" and !member_id != "" then policy = {"operator" : {
    "hostname": !hostname, 
    "name": !node_name,
    "company": !company_name, 
    "local_ip" : !ip,
    "ip": !external_ip, 
    "port" : !anylog_server_port.int, 
    "rest_port": !anylog_rest_port.int, 
    "db type": !db_type,
    "dbms": !default_dbms, 
    "loc": !loc,
    "member": !member_id 
   }
}

# Yes table | enable external IP 
else if !table == "" and !member_id != "" then policy = {"operator" : {
    "hostname": !hostname, 
    "name": !node_name,
    "company": !company_name, 
    "local_ip" : !ip,
    "ip": !external_ip, 
    "port" : !anylog_server_port.int, 
    "rest_port": !anylog_rest_port.int, 
    "db type": !db_type,
    "dbms": !default_dbms, 
    "table": !table, 
    "loc": !loc,
    "member": !member_id
   }
}

else then policy = {"operator" : {
    "hostname": !hostname, 
    "name": !node_name,
    "company": !company_name, 
    "local_ip" : !ip,
    "ip": !external_ip, 
    "port" : !anylog_server_port.int, 
    "rest_port": !anylog_rest_port.int, 
    "db type": !db_type,
    "dbms": !default_dbms, 
    "table": !table, 
    "loc": !loc
   }
}
 


:push-operator: 
on error call push-operator-error 
run client (!master_node) blockchain push !policy 

:wait-for-blockchain: 
blockchain_test = blockchain wait for !policy 
if !blockchain_test == false then goto blockchain-error 

:pull-blockchain; 
on error ignore 
process !anylog_path/AnyLog-Network/anylog_deployment_scripts/blockchain_pull_json.al

end script 

:push-operator-error: 
echo "Failed to push polic: " json !policy 
return 

:blockchain-error: 
echo "Failed to validate policy: " json !policy


