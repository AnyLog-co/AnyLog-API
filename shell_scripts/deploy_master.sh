<<COMMENT
The following is an example of deploying AnyLog Master node using docker run, instead of the API tool.
The deployment process is hard-coded and can be found in volume - ${NODE_NAME}-local-scripts
This means that AnyLog will contain only:
- TCP port
- REST port
- BROKER port (if set)
- Authentication (if set)
- run blockchain sync
- connect to database blockchain & system_query
- create ledger table in blockchain (if DNE)
- create policy if DNE exist in blockchain.ledger
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
NODE_TYPE=master
NODE_NAME=anylog-master-node
COMPANY_NAME=AnyLog Co.
# Networking
# External and local IPs user would like to use if not default on the machine
#EXTERNAL_IP=10.0.0.231
#LOCAL_IP=10.0.0.231
ANYLOG_SERVER_PORT=2048
ANYLOG_REST_PORT=2049
ANYLOG_BROKER_PORT=2050
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
  -e MASTER_NODE=${MASTER_NODE} \
  -e AUTHENTICATION=${AUTHENTICATION} \
  -e USERNAME=${USERNAME} \
  -e PASSWORD=${PASSWORD} \
  -e AUTH_TYPE=${AUTH_TYPE} \
  -e DBMS_TYPE=${DBMS_TYPE} \
  -e DBMS_CONN=${DBMS_CONN} \
  -e DBMS_PORT=${DBMS_PORT} \
  -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw \
  -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \
  -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \
  -v ${NODE_NAME}-local-scripts:/app/AnyLog-Network/local_scripts:rw \
  -it --detach-keys="ctrl-d" --rm anylog:${BUILD}
