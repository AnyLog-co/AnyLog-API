#!/bin/bash
<<COMMENT
The following is intended to as an example of deploying an AnyLog instance of type REST node.
An AnyLog instance of type REST consists of a TCP & REST port as well as MQTT broker if provided.
The code doesn't
COMMENT

if [ $# -eq 2 ]
then
  CONFIG_FILE=${1}
  DOCKER_PASSWD=${2}
else
  echo "Missing config file and docker password"
  exit 1
fi

if [[ -f "${CONFIG_FILE}" ]]
then
  BUILD=$(awk -F "=" '/build_type/ {print $2}' ${CONFIG_FILE})
  if [[ ! ${BUILD} ]] ; then BUILD=develop ; fi

  NODE_NAME=$(awk -F "=" '/node_name/ {print $2}' ${CONFIG_FILE})
  if [[ ! ${NODE_NAME} ]] ; then NODE_NAME=new_node ; fi

  ANYLOG_SERVER_PORT=$(awk -F "=" '/anylog_server_port/ {print $2}' ${CONFIG_FILE})
  if [[ ! ${ANYLOG_SERVER_PORT} ]] ; then ANYLOG_SERVER_PORT=2048 ; fi

  ANYLOG_REST_PORT=$(awk -F "=" '/anylog_rest_port/ {print $2}' ${CONFIG_FILE})
  if [[ ! ${ANYLOG_REST_PORT} ]] ; then ANYLOG_SERVER_PORT=2049 ; fi

  ANYLOG_BROKER_PORT=$(awk -F "=" '/anylog_broker_port/ {print $2}' ${CONFIG_FILE}) # Optional

  AUTHENTICATION=$(awk -F "=" '/authentication/ {print $2}' ${CONFIG_FILE})
  if [[ ${AUTHENTICATION} == on ]]
  then
      USERNAME=$(awk -F "=" '/username/ {print $2}' ${CONFIG_FILE})
      if [[ ! ${USERNAME} ]] ; then USERNAME=anylog ; fi
      PASSWORD=$(awk -F "=" '/password/ {print $2}' ${CONFIG_FILE})
      if [[ ! ${PASSWORD} ]] ; then PASSWORD=demo ; fi
      AUTH_TYPE=$(awk -F "=" '/auth_type/ {print $2}' ${CONFIG_FILE})
      if [[ ! ${AUTH_TYPE} ]] ; then AUTH_TYPE=admin ; fi
  elif [[ ! ${AUTHENTICATION} ]]
  then
    AUTHENTICATION=off
  fi

else
  echo "Using default parameters..."
  BUILD=develop
  NODE_NAME=new-node
  ANYLOG_SERVER_PORT=2048
  ANYLOG_REST_PORT=2049
  ANYLOG_BROKER_PORT=2050
  AUTHENTICATION=off
fi

docker login -u oshadmon -p ${DOCKER_PASSWD}
docker pull oshadmon/anylog:${BUILD}
docker logout

if [[ ${AUTHENTICATION} == off ]]
then
  if [[ ! ${ANYLOG_BROKER_PORT} ]] # deploy AnyLog without broker port
  then
    docker run --network host --name ${NODE_NAME} --rm \
      -e NODE_TYPE=rest \
      -e ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} \
      -e ANYLOG_REST_PORT=${ANYLOG_REST_PORT} \
      -e AUTHENTICATION=${AUTHENTICATION} \
      -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw  \
      -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
      -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
      -v ${NODE_NAME}-local-scripts:/app/AnyLog-Network/local_scripts:rw \
      -d -it --detach-keys="ctrl-d" oshadmon/anylog:${BUILD}
  elif [[ ${ANYLOG_BROKER_PORT} ]] # deploy AnyLog with broker port
  then
    docker run --network host --name ${NODE_NAME} --rm \
      -e NODE_TYPE=rest \
      -e ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} \
      -e ANYLOG_REST_PORT=${ANYLOG_REST_PORT} \
      -e ANYLOG_BROKER_PORT=${ANYLOG_BROKER_PORT}\
      -e AUTHENTICATION=${AUTHENTICATION} \
      -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw  \
      -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
      -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
      -v ${NODE_NAME}-local-scripts:/app/AnyLog-Network/local_scripts:rw \
      -d it --detach-keys="ctrl-d" oshadmon/anylog:${BUILD}
  fi
elif [[ ${AUTHENTICATION} == on ]]
then
    if [[ ! ${ANYLOG_BROKER_PORT} ]] # deploy AnyLog without broker port
  then
    docker run --network host --name ${NODE_NAME} --rm \
      -e NODE_TYPE=rest \
      -e ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} \
      -e ANYLOG_REST_PORT=${ANYLOG_REST_PORT} \
      -e AUTHENTICATION=${AUTHENTICATION} \
      -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw  \
      -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
      -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
      -v ${NODE_NAME}-local-scripts:/app/AnyLog-Network/local_scripts:rw \
      -d -it --detach-keys="ctrl-d" oshadmon/anylog:${BUILD}
  elif [[ ${ANYLOG_BROKER_PORT} ]] # deploy AnyLog with broker port
  then
    docker run --network host --name ${NODE_NAME} --rm \
      -e NODE_TYPE=rest \
      -e ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} \
      -e ANYLOG_REST_PORT=${ANYLOG_REST_PORT} \
      -e ANYLOG_BROKER_PORT=${ANYLOG_BROKER_PORT}\
      -e AUTHENTICATION=${AUTHENTICATION} \
      -e USERNAME=${USERNAME} \
      -e PASSWORD=${PASSWORD} \
      -e AUTH_TYPE=${AUTH_TYPE} \
      -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw  \
      -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
      -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
      -v ${NODE_NAME}-local-scripts:/app/AnyLog-Network/local_scripts:rw \
      -d it --detach-keys="ctrl-d" oshadmon/anylog:${BUILD}
  fi
fi


