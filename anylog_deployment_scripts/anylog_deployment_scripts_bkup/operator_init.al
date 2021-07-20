#=============================================================
# Single Node node Init (recognized as Operator on Blockchain) 
#=============================================================
# process !anylog_path/AnyLog-Network/anylog_deployment_scripts/operator_init.al

#set debug off 
debug on tcp rest
#set traceback on
debug on exception
#set debug interactive
#trace level = 1 blockchain

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


# start tcp & rest 
:connect-ports: 
echo "Connect TCP & REST ports" 
on error goto connect-ports-error
run tcp server !external_ip !anylog_server_port !ip !anylog_server_port
run rest server !ip !anylog_rest_port where timeout=0 
if !local_broker == True then run message broker !ip !anylog_broker_port 

#set reply ip = !reply_ip

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

:pull-master:
echo "Pull from blockchain" 
on error call pull-master-error

run blockchain sync where source = master and time = 15 seconds and dest = file and connection = !master_node

# update blockchain from master
sleep 5 
run blockchain sync 
sleep 15  

# Based on whether cluster is enabled call an operator decleration
# For an enabled_cluster the code adds both a cluster and an operator policies; while a disabled cluster declares only an operator policy
echo "Declare Cluster & Operator nodes as needed" 
on error ignore 
is_operator = blockchain get operator where ip = !external_ip and  company = !company_name and name = !node_name
if not !is_operator then 
do if !enable_cluster == True then process !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_operator_w_cluster.al 
do if !enable_cluster == False then process !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_operator.al 


# for cluster enabled 
:send-db: 
on error call send-db-error
echo "Declare partitions & start operator process" 
# set partitions prior to data getting inserted 
# Example 
# partition dbms_name table_name using timestamp_column by time_range 
#    partition sample_data new_sensor using timestamp by 1 month
test_script = file test !local_scripts/start.al
if !test_script then process !local_scripts/start.al

run operator where create_table = true and update_tsd_info = true and archive = true and distributor = true and master_node = !master_node
run streamer
run data distributor
run data consumer where start_date = -30d
set buffer threshold where write_immediate = true

:start-scheduler: 
on error call start-scheduler-error
run scheduler 1 


:start-mqtt: 
on error goto start-mqtt-error 
echo "Start MQTT (if valid)" 
if !mqtt_enable == False and !mqtt_enable_other == False then  goto end-script 
if !mqtt_enable == False and !mqtt_enable_other == True then goto other-mqtt
if !mqtt_enable == True  and !mqtt_raw_data == False then goto format-mqtt
if !mqtt_enable == True  and !mqtt_raw_data == True then 
do run mqtt client where broker=!mqtt_broker and port=!mqtt_broker_port and user=!mqtt_user and password=!mqtt_password and log=!mqtt_log and topic=!mqtt_topic_name
do goto end-script 


:format-mqtt: 
# Run `run mqtt client` with formatted data based on params 
if !mqtt_column_value_type == int then
do run mqtt client where broker=!mqtt_broker and port=!mqtt_broker_port and user=!mqtt_user and password=!mqtt_password and log=!mqtt_log and topic=(name=!mqtt_topic_name and dbms=!mqtt_topic_dbms and table=!mqtt_topic_table and column.timestamp.timestamp=!mqtt_column_timestamp and column.value.int=!mqtt_column_value)
if !mqtt_column_value_type == timestamp then
do run mqtt client where broker=!mqtt_broker and port=!mqtt_broker_port and user=!mqtt_user and password=!mqtt_password and log=!mqtt_log and topic=(name=!mqtt_topic_name and dbms=!mqtt_topic_dbms and table=!mqtt_topic_table and column.timestamp.timestamp=!mqtt_column_timestamp and column.value.timestamp=!mqtt_column_value)
if !mqtt_column_value_type == bool then
do run mqtt client where broker=!mqtt_broker and port=!mqtt_broker_port and user=!mqtt_user and password=!mqtt_password and log=!mqtt_log and topic=(name=!mqtt_topic_name and dbms=!mqtt_topic_dbms and table=!mqtt_topic_table and column.timestamp.timestamp=!mqtt_column_timestamp and column.value.bool=!mqtt_column_value)
if !mqtt_column_value_type == str then
do run mqtt client where broker=!mqtt_broker and port=!mqtt_broker_port and user=!mqtt_user and password=!mqtt_password and log=!mqtt_log and topic=(name=!mqtt_topic_name and dbms=!mqtt_topic_dbms and table=!mqtt_topic_table and column.timestamp.timestamp=!mqtt_column_timestamp and column.value.str=!mqtt_column_value)

if not !enable_other_mqtt then end script 

:other-mqtt:
# If enabled, code utilizes the same config for MQTT to extract all (other) topics from the broker as raw data 
on error goto other-mqtt-error
mqtt_topic="#"
run mqtt client where broker=!mqtt_broker and port=!mqtt_broker_port and user=!mqtt_user and password=!mqtt_password and log=!mqtt_log and topic=!mqtt_topic

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

:pull-master-error: 
echo "Failed to initiate scheduled process to pull blockchain" 
return 

:send-db-error: 
echo "Failed to send db from operator watch to database" 
return 

:start-scheduler-error:
echo "Failed to start scheduler 1"
return

:start-mqtt-error: 
echo "Failed to start MQTT client"
return

:other-mqtt-error: 
echo "Failed to start MQTT client for '#' topic" 
end script 
