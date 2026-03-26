#--------------------------------------------------------------------------------------------------------------#
# (basic) MQTT process based on configuration
# By default, the Message client params (in set_params.al) are based rand data coming into AnyLog's
# MQTT message broker
#--------------------------------------------------------------------------------------------------------------#
# process !local_scripts/connectors/basic_msg_client.al

on error ignore
if !debug_mode == true then set debug on

if !mqtt_broker == rest then
if !debug_mode.int > 0 then print "set mqtt client connection"
<do run msg client where broker=!mqtt_broker and port=!mqtt_port and user=!mqtt_user and password=!mqtt_passwd and
user-agent=anylog and log=!mqtt_log and topic=(
    name=!msg_topic and
    dbms=!msg_dbms and
    table=!msg_table and
    column.timestamp.timestamp=!msg_timestamp_column and
    column.value=(type=!msg_value_column_type and value=!msg_value_column)
)>
if !mqtt_broker != rest then
<do run msg client where broker=!mqtt_broker and port=!mqtt_port and user=!mqtt_user and password=!mqtt_passwd
and log=!msg_log and topic=(
    name=!msg_topic and
    dbms=!msg_dbms and
    table=!msg_table and
    column.timestamp.timestamp=!msg_timestamp_column and
    column.value=(type=!msg_value_column_type and value=!msg_value_column)
)>
