#!/bin/bash
<<COMMENT
The following takes an INI configuration file & deploys an AnyLog docker container.
If the user adds DOCKER_PASSWORD parameter, then the code will also update the AnyLog image

Note 1: The deployed docker container will use (by default) UTC. To use local time, update the volumes list to contain:
      -v /run/dbus/system_bus_socket:/run/dbus/system_bus_socket:ro
      -v /etc/localtime:/etc/localtime:ro
COMMENT

if [[ $#  -gt 0 ]] && [[ $# -lt 3 ]]
then
    CONFIG_FILE=$1
    DOCKER_PASSWORD=$2
else
  echo "User must declare at least config file (full path), if docker password than the code will update docker image"
fi

if [[ ! -f ${CONFIG_FILE} ]]
then
  echo "Unable to locate config file (${CONFIG_FILE}), can't continue"
  exit 1
fi

# General information
BUILD=$(grep -v ^\# ${CONFIG_FILE} | awk -F "build=" '{print $2}')
if [[ ! ${BUILD} ]]
then
  BUILD=predevelop
fi

NODE_TYPE=$(grep -v ^\# ${CONFIG_FILE} | awk -F "node_type=" '{print $2}')
if [[ ! ${NODE_TYPE} ]]
then
  NODE_TYPE=single-node

elif [[ "${NODE_TYPE}" == *","* ]]
then
  NODE_TYPE=single-node
elif [[ ! ${NODE_TYPE} -eq master ]] && [[ ! ${NODE_TYPE} -eq operator ]] &&
     [[ ! ${NODE_TYPE} -eq publisher ]] && [[ ! ${NODE_TYPE} -eq query ]] &&
     [[ ! ${NODE_TYPE} -eq single-node ]]
then
    NODE_TYPE=single-node
fi

NODE_NAME=$(grep -v ^\# ${CONFIG_FILE} | awk -F "node_name=" '{print $2}')
if [[ ! ${NODE_NAME} ]] ; then NODE_NAME=new-node ; fi

COMPANY_NAME=$(grep -v ^\# ${CONFIG_FILE} | awk -F "company_name=" '{print $2}')
if [[ ! ${COMPANY_NAME} ]] ; then COMPANY_NAME=New-Company ; fi

LOCATION=$(grep -v ^\# ${CONFIG_FILE} | awk -F "location=" '{print $2}')
if [[ ! ${LOCATION} ]] ; then LOCATION="" ; fi

# Authentication
AUTHENTICATION=$(grep -v ^\# ${CONFIG_FILE} | awk -F "authentication=" '{print $2}')
if [[ ! ${AUTHENTICATION} ]]
then
  AUTHENTICATION=off
elif [[ ! ${AUTHENTICATION} -eq off ]] && [[ ! ${AUTHENTICATION} -eq on ]]
then
  AUTHENTICATION=off
elif [[ ${AUTHENTICATION} -eq on ]]
then
  USERNAME=$(grep -v ^\# ${CONFIG_FILE} | awk -F "useername=" '{print $2}')
  if [[ ! ${USERNAME} ]] ; then USERNAME=anylog ; fi
  PASSWORD=$(grep -v ^\# ${CONFIG_FILE} | awk -F "password=" '{print $2}')
  if [[ ! ${PASSWORD} ]]
  then
    PASSWORD=demo
  fi
  AUTH_TYPE=$(grep -v ^\# ${CONFIG_FILE} | awk -F "auth_type=" '{print $2}')
  if [[ ! ${AUTH_TYPE} ]]
  then
    AUTH_TYPE=user
  elif [[ ! ${AUTH_TYPE} -eq admin ]] && [[ ! ${AUTH_TYPE} -eq user ]]
  then
    AUTH_TYPE=user
  fi
  EXPIRATION=$(grep -v ^\# ${CONFIG_FILE} | awk -F "expiration=" '{print $2}')
fi

# Networking
EXTERNAL_IP=$(grep -v ^\# ${CONFIG_FILE} | awk -F "external_ip=" '{print $2}')
LOCAL_IP=$(grep -v ^\# ${CONFIG_FILE} | awk -F "local_ip=" '{print $2}')
MASTER_NODE=$(grep -v ^\# ${CONFIG_FILE} | awk -F "master_node=" '{print $2}')
ANYLOG_SERVER_PORT=$(grep -v ^\# ${CONFIG_FILE} | awk -F "anylog_tcp_port=" '{print $2}')
if [[ ! ${ANYLOG_SERVER_PORT} ]] ; then ANYLOG_SERVER_PORT=2048 ; fi
ANYLOG_REST_PORT=$(grep -v ^\# ${CONFIG_FILE} | awk -F "anylog_rest_port=" '{print $2}')
if [[ ! ${ANYLOG_REST_PORT} ]] ; then ANYLOG_REST_PORT=2049 ; fi
ANYLOG_BROKER_PORT=$(grep -v ^\# ${CONFIG_FILE} | awk -F "anylog_broker_port=" '{print $2}')

# Database
DBMS_TYPE=$(grep -v ^\# ${CONFIG_FILE} | awk -F "db_type=" '{print $2}')
if [[ ! ${DBMS_TYPE} ]]
then
  DBMS_TYPE=sqlite
elif [[ ! ${DBMS_TYPE} -eq psql ]] && [[ ! ${DBMS_TYPE} -eq sqlite ]]
then
  DBMS_TYPE=sqlite
fi

DBMS_CONNECTION=$(grep -v ^\# ${CONFIG_FILE} | awk -F "db_user=" '{print $2}')
if [[ ! ${DBMS_CONNECTION} ]] ; then DBMS_CONNECTION=anylog@127.0.0.1:demo ; fi

DBMS_PORT=$(grep -v ^\# ${CONFIG_FILE} | awk -F "db_port=" '{print $2}')
if [[ ! ${DBMS_PORT} ]] ; then DBMS_PORT=5432 ; fi

# Operator params
if [ "${NODE_TYPE}" == "single-node" ] || [ "${NODE_TYPE}" == "operator" ]
then
  # DBMS & Cluster
  DBMS_NAME=$(grep -v ^\# ${CONFIG_FILE} | awk -F "default_dbms=" '{print $2}')
  if [[ ! ${DBMS_NAME} ]]
  then
    DBMS_NAME=new_db
  fi

  ENABLE_CLUSTER=$(grep -v ^\# ${CONFIG_FILE} | awk -F "default_dbms=" '{print $2}')
  if [[ ! ${ENABLE_CLUSTER} ]]
  then
    ENABLE_CLUSTER=false
  elif [[ ! ${ENABLE_CLUSTER} -eq true ]] && [[ ! ${ENABLE_CLUSTER} -eq false ]]
  then
    ENABLE_CLUSTER=false
  elif [[ ${ENABLE_CLUSTER} -eq true ]]
  then
    CLUSTER_NAME=$(grep -v ^\# ${CONFIG_FILE} | awk -F "cluster_name=" '{print $2}')
    if [[ ! ${CLUSTER_NAME} ]] ; then CLUSTER_NAME=new-cluster ; fi
  fi

  # Partitions
  ENABLE_PARTITION=$(grep -v ^\# ${CONFIG_FILE} | awk -F "enable_partition=" '{print $2}')
  if [[ ! ${ENABLE_PARTITION} ]]
  then
    ENABLE_PARTITION=false
  elif [[ ! ${ENABLE_PARTITION} -eq false ]] && [[ ! ${ENABLE_PARTITION} -eq true ]]
  then
    ENABLE_PARTITION=false
  elif [[ ${ENABLE_PARTITION} -eq true ]]
  then
    PARTITION_COLUMN=$(grep -v ^\# ${CONFIG_FILE} | awk -F "partition_column=" '{print $2}')
    if [[ ! ${PARTITION_COLUMN} ]] ; then PARTITION_COLUMN=timestamp ; fi
    PARTITION_INTERVAL=$(grep -v ^\# ${CONFIG_FILE} | awk -F "partition_interval=" '{print $2}')
    if [[ ! ${PARTITION_INTERVAL} ]] ; then partition_interval=day ; fi
  fi
fi

# MQTT params

if [[ ${DOCKER_PASSWORD} ]]
then
  docker login -u oshadmon -p ${DOCKER_PASSWORD}
  docker pull oshadmon/anylog:${BUILD##*( )}
  docker logout
fi

#MQTT_ENABLE=$(grep -v ^\# ${CONFIG_FILE} | awk -F "mqtt_enable=" '{print $2}')
#
#if [[ ! ${MQTT_ENABLE} ]]
#then
#  MQTT_ENABLE=false
#elif [[ ! ${MQTT_ENABLE} -eq true ]] && [[ ! ${MQTT_ENABLE} -eq false ]]
#then
#  MQTT_ENABLE=false
#elif [[ ${MQTT_ENABLE} -eq true ]]
#then
#  MQTT_CONN=$(grep -v ^\# ${CONFIG_FILE} | awk -F "mqtt_conn_info=" '{print $2}')
#  if [[ ! ${MQTT_CONN} ]]
#  then
#    MQTT_ENABLE=false
#  else
#    MQTT_USER=$(echo ${MQTT_CONN} | awk -F "@" '{print $1}'})
#    MQTT_BROKER=$(echo ${MQTT_CONN} | awk -F "@" '{print $2}' | awk -F ":" '{print $1}')
#    MQTT_PASSWORD=$(echo ${MQTT_CONN} | awk -F ":" '{print $2}')
#  fi
#  MQTT_LOG=$(grep -v ^\# ${CONFIG_FILE} | awk -F "mqtt_log=" '{print $2}')
#  if [[ ! ${MQTT_LOG} ]]
#  then
#    MQTT_LOG=false
#  elif [[ ! ${MQTT_LOG} -eq true ]] && [[ ! ${MQTT_LOG} -eq false ]]
#  then
#    MQTT_LOG=false
#  fi
#  MQTT_TOPIC=$(grep -v ^\# ${CONFIG_FILE} | awk -F "mqtt_topic_name=" '{print $2}')

docker run --network host --name ${NODE_NAME} --privileged \
    -e NODE_TYPE=${NODE_TYPE} \
    -e BUILD=${BUILD} \
    -e NODE_TYPE=${NODE_TYPE} \
    -e NODE_NAME=${NODE_NAME} \
    -e COMPANY_NAME=${COMPANY_NAME} \
    -e LOCATION=${LOCATION} \
    -e AUTHENTICATION=${AUTHENTICATION} \
    -e USERNAME=${USERNAME} \
    -e PASSWORD=${PASSWORD} \
    -e AUTH_TYPE=${AUTH_TYPE} \
    -e EXPIRATION=${EXPIRATION} \
    -e EXTERNAL_IP=${EXTERNAL_IP} \
    -e LOCAL_IP=${LOCAL_IP} \
    -e MASTER_NODE=${MASTER_NODE} \
    -e ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} \
    -e ANYLOG_REST_PORT=${ANYLOG_REST_PORT} \
    -e ANYLOG_BROKER_PORT=${ANYLOG_BROKER_PORT} \
    -e DBMS_TYPE=${DBMS_TYPE} \
    -e DBMS_CONNECTION=${DBMS_CONNECTION} \
    -e DBMS_PORT=${DBMS_PORT} \
    -e DBMS_NAME=${DBMS_NAME} \
    -e ENABLE_CLUSTER=${ENABLE_CLUSTER} \
    -e CLUSTER_NAME=${CLUSTER_NAME} \
    -e ENABLE_PARTITION=${ENABLE_PARTITION} \
    -e PARTITION_COLUMN=${PARTITION_COLUMN} \
    -e PARTITION_INTERVAL=${PARTITION_INTERVAL} \
    -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw \
    -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
    -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
    -d -it --detach-keys="ctrl-d" --rm oshadmon/anylog:${BUILD}
