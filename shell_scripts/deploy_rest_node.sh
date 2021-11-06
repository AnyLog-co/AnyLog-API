<<COMMENT
The following deploys AnyLog with nothing running on it
COMMENT

NODE_NAME=anylog-test-single-node
COMPANY_NAME=AnyLog Co.

ENABLE_CLUSTER=true
CLUSTER_NAME=anylog-test-cluster

if [ $# -eq 1 ]
then
    BUILD=$1
else
    BUILD=predevelop
    echo "Build type is set to predevelop" 
fi



docker run --network host --name ${NODE_NAME} --privileged \
    -e NODE_TYPE=none \
    -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw \
    -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
    -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
    -v /run/dbus/system_bus_socket:/run/dbus/system_bus_socket:ro \
    -v /etc/localtime:/etc/localtime:ro \
    -it --detach-keys="ctrl-d" --rm oshadmon/anylog:${BUILD}


cluster_name        = $CLUSTER_NAME


# network params
anylog_server_port  = $ANYLOG_SERVER_PORT
anylog_rest_port    = $ANYLOG_REST_PORT
if $ANYLOG_BROKER_PORT then anylog_broker_port = $ANYLOG_BROKER_PORT
if $EXTERNAL_IP then external_ip = $EXTERNAL_IP
if $LOCAL_IP    then ip          = $LOCAL_IP
master_node         = $MASTER_NODE

# Database params
dbms_type           = $DBMS_TYPE
dbms_connection     = $DBMS_CONNECTION
dbms_port           = $DBMS_PORT
default_dbms        = $DBMS_NAME

# MQTT
if $MQTT_ENABLE then mqtt_enable = $MQTT_ENABLE
else mqtt_enable = false
if !mqtt_enable != true and !mqtt_enable != false then mqtt_enable=false
else if !mqtt_enable == true then
do mqtt_broker = $MQTT_BROKER
do mqtt_port = $MQTT_PORT
do mqtt_user = $MQTT_USER
do mqtt_password = $MQTT_PASSWORD
do mqtt_log = $MQTT_LOG
do mqtt_topic_name = $MQTT_TOPIC_NAME
do mqtt_topic_dbms = $MQTT_TOPIC_DBMS
do mqtt_topic_table = $MQTT_TOPIC_TABLE
do mqtt_column_timestamp = $MQTT_COLUMN_TIMESTAMP
do mqtt_column_value_type = $MQTT_COLUMN_VALUE_TYPE
do mqtt_column_value = $MQTT_COLUMN_VALUE
