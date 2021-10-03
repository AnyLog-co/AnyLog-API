# Deployment 

The following is intended as a tool to easily deploy AnyLog via REST rather. 
We suggest to review & manipulate the python files as they fit for you. 

```
$HOME/AnyLog-API 
├── config     <-- sample config files 
├── deployment <-- directory containing the main that's intened to be the "default" format for deploying an anylog instance    
├── examples   <-- examples of how to use the code within other programs
├── rest       <-- methods for REST requests 
└── support    <-- Other functions and methods used through out the code (such read/write of configs)
```

## Builds
* **Debian** runs _Ubuntu:18.04_ and is roughly 287.25MB 
* **Alpine** runs _Alpine:3.7_ and is roughly 56.11MB
* By adding **predevelop** before OS version (ex: `predevelop-debian`) you'd run the latest beta version 
 
## Requirements
* [Docker](https://docs.docker.com/engine/install/)
* [Python3](https://www.python.org/downloads/)
  * argparse
  * configparser
  * json
  * os
  * requests
  * sys
  * time
  
**Note**: All Python packages used tend to be standard, thus do not require an installment. However, in case of an issue, 
installment can be done via [pip3](https://www.activestate.com/resources/quick-reads/how-to-install-and-use-pip3/#:~:text=1%20Open%20the%20Control%20Panel%20and%20navigate%20to,and%20add%20the%20directory%20where%20pip3%20is%20installed%2C)  
```buildoutcfg
pip3 install ${PACKAGE_NNAME}
```

## Steps 
0. [Contact us](mailto:info@anylog.co) for a docker password


1. Git clone https://github/AnyLog-co/AnyLog-API


2. Prepare an INI configuration file - can either use [questionnaire](config/questionnaire.sh) or manually copy & update the sample config file ([config.ini](config/config.ini))


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
# Options
AnyLog-API anylog-node$ python3 ~/AnyLog-API/deployment/main.py --help 
usage: main.py [-h] [-a AUTH] [-t TIMEOUT] [-f SCRIPT_FILE] [-u [UPDATE_CONFIG]] [-l [DISABLE_LOCATION]] [-s [STOP_NODE]] [-c [CLEAN_NODE]]
               [-e [EXCEPTION]]
               rest_conn config_file

positional arguments:
  rest_conn             REST connection information
  config_file           AnyLog INI config file

optional arguments:
  -h, --help            show this help message and exit
  -a AUTH, --auth AUTH  REST authentication information (default: None)
  -t TIMEOUT, --timeout TIMEOUT
                        REST timeout period (default: 30)
  -f SCRIPT_FILE, --script-file SCRIPT_FILE
                        If set run commands in file at the end of the deployment (must include path) (default: None)
  -u [UPDATE_CONFIG], --update-config [UPDATE_CONFIG]
                        Whether to update config within AnyLog dictionary (default: False)
  -l [DISABLE_LOCATION], --disable-location [DISABLE_LOCATION]
                        If set to True & location not in config, add lat/long coordinates for new policies (default: True)
  -s [STOP_NODE], --stop-node [STOP_NODE]
                        disconnect node without dropping corresponding policy (default: False)
  -c [CLEAN_NODE], --clean-node [CLEAN_NODE]
                        disconnect node and drop database and policy from blockchain (default: False)
  -e [EXCEPTION], --exception [EXCEPTION]
                        print exception errors (default: False)


# Basic call 
AnyLog-API anylog-node$ python3 $HOME/AnyLog-API/deployment/main.py ${IP}:${PORT} ${CONFIG_FILE}


# Sample call against Publisher node  - start Publisher with an additional file & printing exception errors
AnyLog-API anylog-node$ python3 $HOME/AnyLog-API/deployment/main.py 10.0.0.80:2049 $HOME/AnyLog-API/config/publisher.ini -f $HOME/AnyLog-API/examples/sample_complex_mqtt_call.al -e   
```


**To stop AnyLog docker instance docker**: 
```
docker stop ${NODE_NAME}
```


## Next Steps
1. Improve [configuration](config/config.ini) to support more options. Such as:
   * Blockchain sync time & enable/disable option - currently built in for 1 minute interval (by default)
   * Unique partitions per table - currently all tables have the same partition based on logical database
   * For MQTT support more than one "value" column under a given topic
   * For publisher & operator, the code automatically runs [immidate thresold](https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#setting-and-retrieving-thresholds-for-a-streaming-mode)
   

2. Single execution for [Questionnaire](config/questionnaire.sh) and [docker instance deployment](deploy_node.sh) 
    * Phase 1 - against local machine
    * Phase 2 - against a remote machine


3. Improve comments within code base: 
   * Validate comments are consistent for repeating variables 
   * Add URLs corresponding to different methods
    


