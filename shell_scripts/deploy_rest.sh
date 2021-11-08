<<COMMENT
The following is an example of deploying AnyLog REST node using docker run, instead of the API tool.
It is up to the user to then manipulate the enviorment as they see fit, either manually or via REST
This means that AnyLog will contain only:
- TCP port
- REST port
- BROKER port
- Authentication
COMMENT
if [ $# -gt 0 ] && [ $# -lt 3 ]
then
    BUILD=$1
    DOCKER_PASSWORD=$2
else
    printf "Missing image build type for container to run against.\nUser may also specify password to download and/or update the AnyLog image\n"
    exit 1
fi

# Generall configs
ANYLOG_ROOT_DIR=/app # configured within Dockerfile
NODE_TYPE=rest
NODE_NAME=anylog-rest-node

# Networking
# External and local IPs user would like to use if not default on the machine
#EXTERNAL_IP=10.0.0.231
#LOCAL_IP=10.0.0.231
ANYLOG_SERVER_PORT=2048
ANYLOG_REST_PORT=2049
ANYLOG_BROKER_PORT=2050

# authentication
AUTHENTICATION=true
USERNAME=anylog
PASSWORD=demo
AUTH_TYPE=admin


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
  -e ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} \
  -e ANYLOG_REST_PORT=${ANYLOG_REST_PORT} \
  -e ANYLOG_BROKER_PORT=${ANYLOG_BROKER_PORT} \
  -e AUTHENTICATION=${AUTHENTICATION} \
  -e USERNAME=${USERNAME} \
  -e PASSWORD=${PASSWORD} \
  -e AUTH_TYPE=${AUTH_TYPE} \
  -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw \
  -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
  -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
  -it --detach-keys="ctrl-d" --rm anylog:${BUILD}

