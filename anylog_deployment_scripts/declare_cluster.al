#-------------------------------------------------
# The following is an example how to declare cluster 
# Note, there can be more then on table per cluster. however cluster cannot contain more then one table 
#-------------------------------------------------
# process !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_cluster.al

policy = {"cluster": {
    "company": !company_name,
    "dbms": !default_dbms, 
    "name": !cluster_name,
    "master": !master_node
}}

if !table then policy = {"cluster": {
    "company": !company_name,
    "name": !cluster_name,
    "master": !master_node, 
    "table": !table
}}


:push-cluster: 
on error call push-cluster-error 
is_json = json !policy test 
if !is_json == False then goto blockchain-error
blockchain prepare policy !policy 
run client (!master_node) blockchain push !policy 

:wait-for-blockchain: 
blockchain_test = blockchain wait for !policy 
if !blockchain_test == false then goto blockchain-error 
:pull-blockchain: 
on error ignore 
process !anylog_path/AnyLog-Network/anylog_deployment_scripts/blockchain_pull_json.al

end script 

:push-cluster-error: 
echo "Failed to push polic: " json !policy 
return 

:blockchain-error: 
echo "Failed to validate policy: " json !policy
end script 



