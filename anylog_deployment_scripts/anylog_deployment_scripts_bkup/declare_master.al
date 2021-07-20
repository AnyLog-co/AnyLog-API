#--------------------------------
# Add master to blockchain
#---------------------------------
# process !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_master.al

#set debug off 

:declare-loc: 
on error goto declare-loc-error
if not !loc then
do info = rest get where url = https://ipinfo.io/json
do if !info then loc = from !info bring [loc]
do else loc = "0.0, 0.0"
do if not !loc then loc = "0.0, 0.0"

:declare-master: 
on error ignore
policy = {"master" : {
    "hostname": !hostname,
    "name": !node_name,
    "ip" : !external_ip,
    "local_ip": !ip, 
    "company": !company_name, 
    "port" : !anylog_server_port.int,
    "rest_port": !anylog_rest_port.int,
    "loc": !loc
    }
}

:push-master: 
on error goto push-master-error 
blockchain push !policy

:pull-blockchain: 
on error ignore 
process !anylog_path/AnyLog-Network/anylog_deployment_scripts/blockchain_pull_json.al

end script

:declare-loc-error:
loc  = "0.0, 0.0" 
goto declare-master 


:push-master-error: 
echo "Failed to push master to blockchain" 
goto pull-blockchain 
