create work directories

create table ledger where dbms=blockchain
create table tsd_info where dbms=almgm

# Update the master node policy
blockchain get master where name=!node_name and company=!company_name and ip=!external_ip and port=!anylog_server_port
—> If a policy is not returned:
set new_policy = {"master" : {"hostname": !hostname, "name": !node_name, "ip" : !external_ip, "local_ip": !ip, "company": !company_name, "port" : !anylog_server_port.int, "rest_port": !anylog_rest_port.int, "loc": !loc}}
blockchain prepare policy !new_policy
blockchain insert where policy=!new_policy and local=true and master=!master_node

# Update a cluster policy
blockchain get cluster where name=!cluster_name and company=!company_name bring.first
—> If a policy is not returned:
set new_policy = {"cluster": {"company": !company_name, "dbms": !default_dbms, "name": !cluster_name, "master": !master_node}}
blockchain prepare policy !new_policy
blockchain insert where policy=!new_policy and local=true and master=!master_node
policy =  blockchain get cluster where name = !cluster_name and company=!company_name bring.first
cluster_id = from !policy bring [cluster][id]  # The key cluster_id is assigned with the ID of the cluster policy.

# Update an Operator policy
set new_policy = {"operator": {"hostname": !hostname, "name": !node_name, "company": !company_name, "local_ip": !ip, "ip": !external_ip, "port" : !anylog_server_port.int, "rest_port": !anylog_rest_port.int, "loc": !loc, "cluster": !cluster_id}}
if not !cluster_id then new_policy = {"operator": {"hostname": !hostname, "name": !node_name, "company": !company_name, "local_ip" : !ip, "ip": !external_ip, "port" : !anylog_server_port.int, "rest_port": !anylog_rest_port.int, "dbms": !default_dbms, "loc": !loc}}
policy = blockchain get operator where name=!node_name and company=!company_name and ip=!external_ip and port=!anylog_server_port and cluster = !cluster_id
—> If a policy is not returned:
blockchain prepare policy !new_policy
blockchain insert where policy=!new_policy and local=true and master=!master_node
