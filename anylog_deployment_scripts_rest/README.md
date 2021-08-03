# Deployment 

The following is intended as a tool to easily deploy AnyLog via REST rather. 
We suggest to review to manipulate the python files as they fit for you. 


## Builds
* **Debian** runs _Ubuntu:18.04_ and is roughly 287.25MB 
* **Alpine** runs _Alpine:3.7_ and is roughly 56.11MB
* By adding **predevelop** before OS version (ex: `predevelop-debian`) you'd run the latest beta version 
 
## Issues: 
* Code validates the request went through smoothly, it doesn't check whether the process was actually successful

## Steps 
0. Contact us for a docker password [info@anylog.co](mailto:info@anylog.co)
1. Git clone https://github/AnyLog-co/anylog-deployment
2. Prepare INI config files 
3. Start AnyLog 
4. Use REST to configure a type of node 

## Sample Docker Call 
```
export NODE_NAME=new-node
export SERVER_PORT=2048
export REST_PORT=2049 
export BROKER_PORT=2050 # optional

docker run --network host --name ${NODE_NAME} \
    -e NODE_TYPE=rest \
    -e ANYLOG_SERVER_PORT=${SERVER_PORT} \
    -e ANYLOG_REST_PORT=${REST_PORT} \
    [-e ANYLOG_BROKER_PORT=${BROKER_PORT}] \ 
    -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw \ 
    -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \ 
    -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \ 
    -d oshadmon/anylog:${BUILD_TYPE}  
```
**Note**: When using interactive mode (`-it`) user should add `--detach-keys="ctrl-d"` 



**Attach to Docker**: `docker attach --detach-keys="ctrl-d"  ${CONTAINER_ID}` 

**Detach from Docker**: `CTRL+d`  
