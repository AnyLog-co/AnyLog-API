# Deployment 

The following is intended as a tool to easily deploy AnyLog via REST rather. 
We suggest to review & manipulate the python files as they fit for you. 

```
$HOME/AnyLog-API 
├── config     <-- sample config files 
├── deployment <-- main code for deploying AnyLog via REST   
├── examples   <-- Examples of how to use the code in other programs
├── rest       <-- methods for REST requests 
└── support    <-- support methods 
```

## Builds
* **Debian** runs _Ubuntu:18.04_ and is roughly 287.25MB 
* **Alpine** runs _Alpine:3.7_ and is roughly 56.11MB
* By adding **predevelop** before OS version (ex: `predevelop-debian`) you'd run the latest beta version 
 
## Steps 
0. [Contact us](mailto:info@anylog.co) for a docker password


1. Git clone https://github/AnyLog-co/AnyLog-API


2. Prepare INI [config files](config/) - can use [questionnaire](config/questionnaire.sh)


3. [Deploy AnyLog](deploy_node.sh) for REST Interface - we suggest to begin with interactive mode and detach once the node is up.
```
export NODE_NAME=new-node
export SERVER_PORT=2048
export REST_PORT=2049 
export BROKER_PORT=2050 # optional

docker run --network host --name ${NODE_NAME} --rm \
    -e NODE_TYPE=rest \
    -e ANYLOG_SERVER_PORT=${SERVER_PORT} \
    -e ANYLOG_REST_PORT=${REST_PORT} \
    -e ANYLOG_BROKER_PORT=${BROKER_PORT 
    -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw \ 
    -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw \ 
    -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw \ 
    -v ${NODE_NAME}-local-scripts:/app/AnyLog-Network/local_scripts:rw \
    -it --detach-keys="ctrl-d" oshadmon/anylog:predevelop
```
**Attach to Docker**: `docker attach --detach-keys="ctrl-d"  ${CONTAINER_ID}`

**Detach from Docker**: `CTRL+d`


4. Use REST to configure an AnyLog instance
```
python3 $HOME/AnyLog-API/deployment/main.py ${IP}:${PORT} ${CONFIG_FILE} 
```


**To stop AnyLog docker instance docker**: 
```
docker stop ${NODE_NAME}
```


## Next Steps
1. Single execution for [Questionnaire](config/questionnaire.sh) and [docker instance deployment](deploy_node.sh) 
    * Phase 1 - against local machine
    * Phase 2 - against a remote machine
   

2. Improve [configuration](config/config.ini) to support more options. Such as:
   * blockchain sync time
   * unique partitions per table 
   * For MQTT support more than one "value" column under a given topic

