#=============================================================
# Single Node node Init (recognized as Operator on Blockchain) 
#=============================================================
# process !anylog_path/AnyLog-Network/anylog_deployment_scripts/publisher_init.al

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
if !local_broker == True then run message broker !external_ip !anylog_broker_port !ip !anylog_broker_port 
#set reply ip = !reply_ip

# connect to databases 
:connect-dbms: 
echo "Connect Databases" 
on error call connect-dbms-error 
db_name = "system_query"
connect dbms sqlite !db_user !db_port system_query memory

db_name = "almgm"
connect dbms sqlite !db_user !db_port !db_name

:pull-master:
echo "Declare Publisher" 
on error call pull-master-error
run blockchain sync where source = master and time = 30 seconds and dest = file and connection = !master_node

on error ignore 
is_publisher = blockchain get publisher where ip = !external_ip and  company = !company_name and name = !node_name 

if not !is_publisher then thread !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_publisher.al 


:send-operator:
# send data in publisher watch_dir to operator on   
# if fails to send file is transfered to error_dir
on error call send-operator-error 
echo "Start Publisher Process" 
company = *
run publisher where compress_json = true and move_json = true and master_node = !master_node and dbms_name = file_name[0] and table_name = file_name[1]
set buffer threshold where write_immediate = true
run streamer 
test_script = file test !local_scripts/start.al
if !test_script == true then process !local_scripts/start.al

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

if not !enable_othr_mqtt then end script 

:other-mqtt:
# If enabled, code utilizes the same config for MQTT to extract all (other) topics from the broker as raw data 
on error goto other-mqtt-error
mqtt_topic="#"
run mqtt client where broker=!mqtt_broker and port=!mqtt_broker_port and user=!mqtt_user and password=!mqtt_password and log=!mqtt_log and topic=!mqtt_topic

:end-script:
end script

:pull-master-error:
echo "Failed to initiate scheduled process to pull blockchain"
return

:connect-ports-error:
echo "Failed to connect to TCP or REST"
echo "As such, cannot continue with script" 
end script 

:connect-dbms-error: 
echo "Failed to connect to dbms " + !db_name
return

:send-operator-error: 
echo "Failed to initiate transfer from publisher to operator" 
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
