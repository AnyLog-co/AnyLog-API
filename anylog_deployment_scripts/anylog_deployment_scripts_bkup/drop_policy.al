#--------------------------------------------------
# The following process is intended to drop policy 
#--------------------------------------------------
# process !anylog_path/AnyLog-Network/anylog_deployment_scripts/drop_policy.al

:get-policy: 
on error goto get-node-error 
node = blockchain get $NODE_TYPE where ip = !ip and company = !company_name and name = !node_name 
if $NODE_TYPE == operator then cluster_id = from !node bring [operator][cluster] 

:drop-policy: 
on error call drop-policy-error 
run client (!master_node) blockchain drop policy !node 

:get-blockchain: 
on error ignore 
process !anylog_path/AnyLog-Network/anylog_deployment_scripts/blockchain_pull_json.al

sleep 5 

:validate-drop: 
on error goto validate-drop-eror 
new_node = blockchain get $NODE_TYPE where ip = !ip and company = !company_name and name = !node_name 
if not !new_node then echo "success" 


:drop-cluster: 
# if NODE_TYPE is operator then get cluster_id and goto drop_cluster script
on error ignore 
if $NODE_TYPE == operator then 
do cluster_id = from !node bring [operator][cluster] 
do if !cluster_id then process !anylog_path/AnyLog-Network/anylog_deployment_scripts/drop_cluster.al 

end script 



:get-policy-error:
echo "failed to get valid policy" 
end script 

:drop-policy-error: 
echo "failed to echo policy"
return 

:validate-drop-error: 
echo "failed to validate policy drop" 
end script 

