#-----------------------------------------------------------------------------------------------------------------------
# Sample MQTT policy for REST / MQTT that's policy based - based on  basic_mqtt.al
# By default, the Message client params (in set_params.al) are based rand data coming into AnyLog's
# MQTT message broker
#-----------------------------------------------------------------------------------------------------------------------
# process !local_scripts/demo-scripts/basic_msg_client_policy.al

on error ignore

set create_policy = false

:preparre-policy:
policy_id = basic-mqtt
policy = blockchain get mapping where id = !policy_id
if !policy then goto msg-call
if !create_policy == true then goto declare-policy-error

<new_policy = {
    "mapping"; {
        "id": !policy_name,
        "dbms": !msg_dbms,
        "table': !msg_table,
        "readings": "",
        "schema": {
            "timestamp": {
                "type": "timestamp",
                "default": !msg_timestamp_column
            },
            "value": {
                "type": !msg_value_column_type,
                "value": !msg_value_column
            }
        }
    }
}>

:publish-policy:
process !local_scripts/policies/publish_policy.al
if !error_code == 1 then goto sign-policy-error
if !error_code == 2 then goto prepare-policy-error
if !error_code == 3 then goto declare-policy-error
set create_policy = true
goto check-policy


:msg-call:
on error goto msg-error
if not !anylog_broker_port and !user_name and !user_password then
<do run msg client where broker=rest and port=!anylog_rest_port and user=!user_name and password=!user_password and user-agent=anylog and log=false and topic=(
    name=!policy_id and
    policy=!policy_id
)>
else if !anylog_broker_port then
<do run msg client where broker=local and port=!anylog_broker_port and log=false and topic=(
    name=!policy_id and
    policy=!policy_id
)>
else if not !anylog_broker_port then
<do run msg client where broker=rest and port=!anylog_rest_port and user-agent=anylog and log=false and topic=(
    name=!policy_id and
    policy=!policy_id
)>

:end-script:
end script

:terminate-scripts:
exit scripts

:sign-policy-error:
print "Failed to sign master policy"
goto terminate-scripts

:prepare-policy-error:
print "Failed to prepare member master policy for publishing on blockchain"
goto terminate-scripts

:declare-policy-error:
print "Failed to declare master policy on blockchain"
goto terminate-scripts

:msg-error:
echo "Failed to deploy MQTT process"
goto end-script
