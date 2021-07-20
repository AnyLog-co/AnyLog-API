# Sample call: docker run --network host --name test -e NODE_TYPE=rest -e ANYLOG_SERVER_PORT=2048 -e ANYLOG_REST_PORT=2049 [--ANYLOG_BROKER_PORT=2050] -it oshadmon/anylog:[alpine || debian]

on error ignore 

anylog_root_dir     = $ANYLOG_ROOT_DIR 
anylog_server_port  = $ANYLOG_SERVER_PORT 
anylog_rest_port    = $ANYLOG_REST_PORT 

set anylog home $ANYLOG_ROOT_DIR
set authentication off

run tcp server !external_ip $ANYLOG_SERVER_PORT !ip $ANYLOG_SERVER_PORT 
run rest server !ip $ANYLOG_REST_PORT 

if $ANYLOG_BROKER_PORT then 
do anylog_broker_port = $ANYLOG_BROKER_PORT 
do run message broker !external_ip !anylog_broker_port !ip !anylog_broker_port

