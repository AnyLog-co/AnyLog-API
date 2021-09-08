#!/bin/bash
<<COMMENT
The following is intended to as an example of deploying an AnyLog instance of type REST node.
An AnyLog instance of type REST consists of a TCP & REST port as well as MQTT broker if provided.
COMMENT

DOCKER_PASSWD=9a707755-32ab-4fb7-87c6-f4891a784bed
BUILD=predevelop
NODE_NAME=new-node
ANYLOG_SERVER_PORT=2048
ANYLOG_REST_PORT=2049
ANYLOG_BROKER_PORT=2050 # Optional - used in 2nd example

docker login -u oshadmon -p ${DOCKER_PASSWD}
docker pull oshadmon/anylog:${BUILD}
docker logout

# The following is an example of a connection using interactive mode. In such a case we suggest running AnyLog within a screeen
docker run --network host --name ${NODE_NAME} --rm \
  -e NODE_TYPE=rest \
  -e ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} -e ANYLOG_REST_PORT=${ANYLOG_REST_PORT} \
  -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw  \
  -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
  -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
  -it  --detach-keys="ctrl-d" oshadmon/anylog:${BUILD}

<<COMMENT
# The following is an example of a connection using detached mode and with an MQTT broker.
docker run --network host --name ${NODE_NAME} --rm \
  -e NODE_TYPE=rest \
  -e ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} -e ANYLOG_REST_PORT=${ANYLOG_REST_PORT} -e ANYLOG_BROKER_PORT=${ANYLOG_BROKER_PORT}\
  -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw  \
  -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
  -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
  -d --detach-keys="ctrl-d" oshadmon/anylog:${BUILD}
COMMENT
