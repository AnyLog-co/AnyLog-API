<<COMMENT
The following is an example of deploying AnyLog Publisher node using docker run, instead of the API tool.
The deployment process is hard-coded and can be found in volume - ${NODE_NAME}-local-scripts.

This specific deployment provides an example of having:
  - REST authentication
  - an MQTT client against the REST (port 2249)
COMMENT

if [ $# -gt 0 ] && [ $# -lt 3 ]
then
    BUILD=$1
    DOCKER_PASSWORD=$2
else
    printf "Missing image build type for container to run against.\nUser may also specify password to download and/or update the AnyLog image\n"
    exit 1
fi

# General configs
ANYLOG_ROOT_DIR=/app # configured within Dockerfile
NODE_TYPE=publisher
NODE_NAME=anylog-publisher-rest-node
COMPANY_NAME=AnyLog

# Networking
# External and local IPs user would like to use if not default on the machine
#EXTERNAL_IP=10.0.0.231
#LOCAL_IP=10.0.0.231
ANYLOG_SERVER_PORT=2248
ANYLOG_REST_PORT=2249
MASTER_NODE=10.0.0.231:2048

# authentication
AUTHENTICATION=true
USERNAME=anylog
PASSWORD=demo
AUTH_TYPE=admin

# database
DBMS_TYPE=sqlite
DBMS_CONN=anylog@127.0.0.1:demo
DBMS_PORT=5432

# MQTT params
ENABLE_MQTT=true
MQTT_BROKER=rest
MQTT_PORT=2249
MQTT_USER=anylog
MQTT_PASSWORD=demo
MQTT_LOG=true
MQTT_TOPIC_NAME=rest-topic
MQTT_TOPIC_DBMS="bring [dbms]"
MQTT_TOPIC_TABLE="bring [table]"
MQTT_COLUMN_TIMESTAMP="bring [timestamp]"
MQTT_COLUMN_VALUE_TYPE=float
MQTT_COLUMN_VALUE="bring [value]"


if [[ ${DOCKER_PASWORD} ]]
then
  docker login -u oshadmon -p ${DOCKER_PASSWORD}
  docker pull oshadmon/anylog:${BUILD}
  docker logout
fi

docker run --network host --name ${NODE_NAME} --privileged \
  -e ANYLOG_ROOT_DIR=${ANYLOG_ROOT_DIR} \
  -e NODE_TYPE=${NODE_TYPE} \
  -e NODE_NAME=${NODE_NAME} \
  -e COMPANY_NAME=${COMPANY_NAME} \
  -e ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} \
  -e ANYLOG_REST_PORT=${ANYLOG_REST_PORT} \
  -e MASTER_NODE=${MASTER_NODE} \
  -e AUTHENTICATION=${AUTHENTICATION} \
  -e USERNAME=${USERNAME} \
  -e PASSWORD=${PASSWORD} \
  -e AUTH_TYPE=${AUTH_TYPE} \
  -e DBMS_TYPE=${DBMS_TYPE} \
  -e DBMS_CONN=${DBMS_CONN} \
  -e DBMS_PORT=${DBMS_PORT} \
  -e ENABLE_MQTT=${ENABLE_MQTT} \
  -e MQTT_BROKER=${MQTT_BROKER} \
  -e MQTT_PORT=${MQTT_PORT} \
  -e MQTT_USER=${MQTT_USER} \
  -e MQTT_PASSWORD=${MQTT_PASSWORD} \
  -e MQTT_LOG=${MQTT_LOG} \
  -e MQTT_TOPIC_NAME=${MQTT_TOPIC_NAME} \
  -e MQTT_TOPIC_DBMS=${MQTT_TOPIC_DBMS} \
  -e MQTT_TOPIC_TABLE=${MQTT_TOPIC_TABLE} \
  -e MQTT_COLUMN_TIMESTAMP=${MQTT_COLUMN_TIMESTAMP} \
  -e MQTT_COLUMN_VALUE_TYPE=${MQTT_COLUMN_VALUE_TYPE} \
  -e MQTT_COLUMN_VALUE=${MQTT_COLUMN_VALUE} \
  -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw \
  -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
  -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
  -v ${NODE_NAME}-local-scripts:/app/AnyLog-Network/local_scripts:rw \
  -it --detach-keys="ctrl-d" --rm anylog:${BUILD}
