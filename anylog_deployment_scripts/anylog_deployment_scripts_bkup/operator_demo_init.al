#=============================================================
# Single Node node Init (recognized as Operator on Blockchain) 
#=============================================================
# process !anylog_path/AnyLog-Network/anylog_deployment_scripts/operator_init.al

#set debug off 

# This hides any messages sent to the node 
# To view messages: user should call 'get echo queue' 
set echo queue on

set anylog home $ANYLOG_ROOT_DIR
process !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_params.al

# start tcp & rest 
:connect-ports: 
echo "Connect TCP & REST ports" 
on error goto connect-ports-error
run tcp server !external_ip !anylog_server_port !ip !anylog_server_port
run rest server !ip !anylog_rest_port where timeout=0 

# connect to databases 
:connect-dbms: 
echo "Connect Databases" 
on error call connect-dbms-error 

if !default_dbms == '' then 
do echo "Operator must contain a default DBMS" 
do end script

db_name = !default_dbms 
connect dbms !db_type !db_user !db_port !db_name 

db_name = "system_query" 
connect dbms sqlite !db_user !db_port system_query memory 

db_name = "almgm"
connect dbms !db_type !db_user !db_port !db_name

on error call connect-almgm-error
create table tsd_info where dbms = !db_name 

:pull-blockchain: 
echo "Declare Cluster & Operator nodes as needed" 
on error ignore
process !anylog_path/AnyLog-Network/anylog_deployment_scripts/blockchain_pull_json.al 

:create-table: 
on error call create-table-error
create table create table ping_sensor where dbms = !default_dbms 

# Based on whether cluster is enabled call an operator decleration
# For an enabled_cluster the code adds both a cluster and an operator policies; while a disabled cluster declares only an operator policy
on error ignore 
if !enable_cluster == True then thread !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_operator_w_cluster.al 
if !enable_cluster == False then thread !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_operator.al 
 
# for cluster enabled 
:send-db: 
on error call send-db-error
echo "Declare partitions & start operator process" 
# set partitions prior to data getting inserted 
# Example 
# partition dbms_name table_name using timestamp_column by time_range 
#    partition sample_data new_sensor using timestamp by 1 month

run operator where compress_json = true and move_json = true and create_table = true and  update_tsd_info = true and master_node = !master_node

:start-mqtt: 
on error goto start-mqtt-error 
if !enable_mqtt == True then 
do run mqtt client where broker=!mqtt_broker and port=!mqtt_port and user=!mqtt_user and password=!mqtt_password and log=!mqtt_log and topic=(name=!mqtt_topic and dbms=!company_name and table = "bring [metadata][machine_name] _ [metadata][serial_number]" and column.timestamp.timestamp = "bring [ts]" and column.value.int = "bring [value]") 
do run streamer 

:pull-master:
on error call pull-master-error
run blockchain sync where source = master and time = 30 seconds and dest = file and connection = !master_node

:end-script:
end script 

:connect-ports-error: 
echo "Failed to connect to TCP or REST" 
echo "As such, cannot continue setting up node" 
exit 

:connect-dbms-error: 
echo "Failed to connect to dbms " + !db_name 
return  

:connect-almgm-error:
echo "Failed to create table for tsd_info on " + !db_name
return 

:send-db-error: 
echo "Failed to create table" 
return 

:pull-master-error: 
echo "Failed to initiate scheduled process to pull blockchain" 
return 

:send-db-error: 
echo "Failed to send db from operator watch to database" 
return 


:start-mqtt-error: 
echo "Failed to start MQTT client"
return
