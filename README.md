# Deployment 

The following is intended as a tool to easily deploy AnyLog via REST rather. 
We suggest to review & manipulate the python files as they fit for you. 

```
$HOME/AnyLog-API 
├── config     <-- sample config files 
├── deployment <-- main code for deploying AnyLog via REST   
├── rest       <-- methods for REST requests 
└── support    <-- support metthods 
```

## Builds
* **Debian** runs _Ubuntu:18.04_ and is roughly 287.25MB 
* **Alpine** runs _Alpine:3.7_ and is roughly 56.11MB
* By adding **predevelop** before OS version (ex: `predevelop-debian`) you'd run the latest beta version 
 
## Steps 
0. Contact us for a docker password [info@anylog.co](mailto:info@anylog.co)

1. Git clone https://github/AnyLog-co/AnyLog-API

2. Prepare INI [config files](config/) 

3. Update [deployment](deployment/) scripts for your system 

4. Start AnyLog for REST Interface - we suggest to run interacive within screen
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
    -it oshadmon/anylog:osdev
```

5. Use REST to configure an AnyLog instance
```
python3 $HOME/AnyLog-API/deployment/main.py ${IP}:${PORT} ${CONFIG_FILE} 
```
 
