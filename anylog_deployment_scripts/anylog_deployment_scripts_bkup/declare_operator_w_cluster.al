#----------------------------------------------------------------------------
# The following declares cluster/operator combo if enable_cluster is set True 
# Steps 
#     1. Validate table is set 
#     2. check if cluster exists  
#     3. If cluster DNE delcare cluster policy
#     4. Get cluster_id   
#     6. Validate !cluster_id was given and declare operator 
#        If !cluster_id doesn't exist wait 10 sec and repeat (repeat occrus oce) 
#----------------------------------------------------------------------------
# process !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_operator_w_cluster.al

#set debug off 
# Validate table(s) values set 

:validate-table: 
on error ignore 
if !table  == '' then goto validate-table-error 

:get-cluster: 
on error ignore 
if !cluster_id then is_cluster = blockchain get cluster where id = !cluster_id 
else is_cluster = blockchain get cluster where name = !cluster_name and company = !company_name

if not !is_cluster then process !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_cluster.al 

sleep 10 
run client (!master_node) blockchain pull to json !!blockchain_file
run client (!master_node) file get !!blockchain_file !blockchain_file 

is_cluster = blockchain get cluster where name = !cluster_name and company = !company_name

:declare-operator: 
cluster_id = from !is_cluster bring [cluster][id]

if !cluster_id then process !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_cluster_operator.al 

end script 

:validate-table-error: 
echo "Error: For cluster table must be declared in operator config" 
end script 

