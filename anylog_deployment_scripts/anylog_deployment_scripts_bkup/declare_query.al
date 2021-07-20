#--------------------------------
# Add query to blockchain
#---------------------------------
# process !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_query.al


#set debug off 
:declare-loc: 
on error goto declare-loc-error
if not !loc then 
do info = rest get where url = https://ipinfo.io/json
do if !info then loc = from !info bring [loc]
do else loc = "0.0, 0.0"
do if not !loc then loc = "0.0, 0.0"

:declare-query:
policy = {"query" : {
    "hostname": !hostname,
    "name": !node_name,
    "company": !company_name, 
    "ip" : !external_ip,
     
    "port" : !anylog_server_port.int,
    "rest_port": !anylog_rest_port.int, 
    "db type": !db_type,
    "loc": !loc
    }
} 

:push-query: 
on error call push-query-error 
run client (!master_node) blockchain push !policy 

:wait-for-blockchain: 
blockchain_test = blockchain wait for !policy 
if !blockchain_test == false then goto blockchain-error 

:pull-blockchain; 
on error ignore 
process !anylog_path/AnyLog-Network/anylog_deployment_scripts/blockchain_pull_json.al

end script 

:push-query-error: 
echo "Failed to push polic: " json !policy 
return 

:blockchain-error: 
echo "Failed to validate policy: " json !policy


