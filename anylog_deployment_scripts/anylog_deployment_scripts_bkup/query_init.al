#=============================================================
# Single Node node Init (recognized as Operator on Blockchain) 
#=============================================================
# process !anylog_path/AnyLog-Network/demo/query_init.al

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
if !set_authentication == True then
do set authentication on 
do id add user where name=!authentication_user and type=admin and passwor=!authentication_passwd 
else set authentication off 


# Enable SMTP client 
#run smtp client where email=alerts@anylog.co and password=alerts4AnyLog!

error_code = 0 

# start tcp & rest 
:connect-ports: 
echo "Connect TCP & REST" 
on error call connect-ports-error
run tcp server !external_ip !anylog_server_port !ip !anylog_server_port
run rest server !ip !anylog_rest_port where timeout=0 
#set reply ip = !reply_ip

# connect to databases 
:connect-dbms: 
echo "Declare Databases" 
on error call connect-dbms-error 

connect dbms !db_type !db_user !db_port system_query memory

:pull-master:
on error call pull-master-error
run blockchain sync where source = master and time = 15 seconds and dest = file and connection = !master_node

on error ignore 
is_query = blockchain get query where hostname = !hostname and ip = !external_ip 
if not !is_query then thread !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_query.al 

:start-scheduler: 
on error call start-scheduler-error
run scheduler 1 


:end-script:
end script

:pull-master-error:
echo "Failed to initiate scheduled process to pull blockchain"
return

:connect-ports-error:
echo "Failed to connect to TCP or REST" 
echo "As such, cannot continue setting up node" 
end script 

:connect-dbms-error: 
echo "Failed to connect to system_query on " !db_type   
echo "Process failed on an issue that's not the physical connection process" 
return

:start-scheduler-error:
echo "Failed to start scheduler 1"
return
