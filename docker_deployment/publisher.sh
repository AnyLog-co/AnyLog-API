export NODE_NAME=publisher
export SERVER_PORT=2248
export REST_PORT=2249 
export BROKER_PORT=2250 # optional

docker run --network host --name ${NODE_NAME} -e NODE_TYPE=rest -e ANYLOG_SERVER_PORT=${SERVER_PORT} -e ANYLOG_REST_PORT=${REST_PORT} -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw    -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw -it oshadmon/anylog:predevelop

