#---------------------------------------
# Drop cluster if no correlated operators
#---------------------------------------
# process !anylog_path/AnyLog-Network/anylog_deployment_scripts/drop_cluster.al

:get-operators: 

on error call get-operators-error
operators = blockchain get operator where cluster = !cluster_id 

:drop-policy:
on error call drop-policy-error 
# If there arne't any connected operators remove cluster 
#  else "exit"
if not !operators then 
do node = blockchain get cluster where id = !cluster_id 
do run client (!master_node) blockchain drop policy !node where id = !cluster_id 
else end script 

:get-blockchain: 
on error ignore 
process !anylog_path/AnyLog-Network/anylog_deployment_scripts/blockchain_pull_json.al

sleep 5 

:validate-drop: 
on error goto validate-drop-eror 
new_node = blockchain get cluster where id = !cluster_id  
if not !new_node then echo "success" 

end script 

:get-cluster-id-error: 
echo "failed to get cluster id from original operator" 
end script 

:get-operators-eror: 
echo "failed to get operators with given cluster id; will remove policy" 
return 

:drop-policy-error: 
echo "failed to drop policy. will validate" 
return 

:validate-drop-error:
echo "failed to validate if policy was dropped" 
end script 

