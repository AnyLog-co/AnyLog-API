#========================================================
# Master node Init  
#========================================================
# process !anylog_path/AnyLog-Network/anylog_deployment_scripts/master_init.al


#set debug off 
debug on tcp rest
#set traceback on
debug on exception
#set debug interactive

# This hides any messages sent to the node 
# To view messages: user should call 'get echo queue' 
set echo queue on

set anylog home $ANYLOG_ROOT_DIR
process !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_params.al  

# Set authentication state  
on error goto disable-authenticaton
if !set_authentication == True then
do set authentication on 
do id add user where name=!authentication_user and type=admin and passwor=!authentication_passwd 
do goto network-connection
else goto disable-authenticaton 

:disable-authenticaton:
set authentication off 

# Enable SMTP client 
#run smtp client where email=alerts@anylog.co and password=alerts4AnyLog!


# start tcp & rest 
:network-connection: 
echo "Connect TCP & REST" 
on error goto network-connection-error
run tcp server !external_ip !anylog_server_port !ip !anylog_server_port
run rest server !ip !anylog_rest_port where timeout=0
#set reply ip = !reply_ip

# connect to databases 
:database-connection: 
echo "Connect Databases" 
on error goto database-coonnection-error  
connect dbms !db_type !db_user !db_port blockchain 
connect dbms sqlite !db_user !db_port system_query memory 

:declare-blockchain: 
on error goto declare-blockchain-error
is_blockchain_table = info table blockchain ledger exists
if !is_blockchain == False  then goto add-master 

# if !is_blockchain then - 
echo "Declare master on blockchain" 
on error ignore 
blockchain pull to json !blockchain_file

on error goto declare-blockchain-error
is_master = blockchain get master 
if !is_master == "" then goto add-master 

is_ip = from !is_master bring ['master']['ip']  
if !ip == !is_ip then end script 

:add-master: 
on error call create-table-error 
create table ledger where dbms = blockchain 

on error ignore
blockchain pull to json !blockchain_file 
is_master = blockchain get master 
if not !is_master then thread !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_master.al 

:blockchain-sync: 
on error goto blockchain-synch-error
run blockchain sync where source = dbms and time = 30 seconds and dest = file 

:start-scheduler: 
on error call start-scheduler-error
run scheduler 1 


:end-script: 
end script 

:network-connection-error: 
echo "Failed to connect to either TCP or REST" 
echo "As such, cannot continue setting up node" 
end script 

:database-connection-error: 
echo "Failed to connect to databases" 
end script

:declare-blockchain-error: 
echo "Faild verify master on blockchain. Will try to add master to blockchain" 
goto add-master 

:pull-master-error:
echo "Failed to initiate scheduled process to pull blockchain"
return

:blockchain-synch-error: 
echo "Failed to init synch process between database & file" 
end script 

:start-scheduler-error:
echo "Failed to start scheduler 1"
return
