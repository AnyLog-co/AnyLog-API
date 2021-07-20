#-----------------------------------------------------------------------------------------------
# Pull blockchain from master. 
# If error is reached, then error in the file transfer as blockchain exists by default on master 
#-----------------------------------------------------------------------------------------------
# process !anylog_path/AnyLog-Network/anylog_deployment_scripts/blockchain_pull_json.al

#set debug off 
on error goto blockchain-error

i = 0 
echo "getting blockchain data from master" 

:wait-for-blockchain: 
run client (!master_node) blockchain pull to json !!blockchain_file
run client (!master_node) file get !!blockchain_file !blockchain_file
is_blockchain = blockchain test 
if !is_blockchain then end script 
if !i > 10 then goto blockchain-error
sleep 2
set i = incr !i 
goto wait-for-blockchain  

end script 

:blockchain-error: 
echo "Error getting blockchain from master (" + !master_node +")" 
end script 
