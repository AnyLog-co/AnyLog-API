# Deployment 

The following is intended as a tool to easily deploy AnyLog via REST using Python. 

A user can either run `$HOME/AnyLog-API/deployment/main.py` (with the appropriate configs) to deploy AnyLog, or utilize 
this code in order to support AnyLog from within their project(s). 

```
$HOME/AnyLog-API
├── config              <-- Sample INI files 
├── deployment          <-- Code used to deploy AnyLog via REST 
├── examples             
│   ├── MQTT            <-- Sample MQTT client commands using .al file  
│   ├── blockchain      <-- Sample scripts to add / remove data from blockchain using rest 
│   └── data            <-- Sample scripts to add data into AnyLog 
├── rest                <-- Rest calls against AnyLog   
├── shell_scripts       <-- Shell scripts to install Docker and deploy AnyLog, Grafana and Postgres instead of via python3
└── support             <-- Support scripts for AnyLog-API, such as creating a policy object & reading config file  
``` 

##Requirements
* [Docker](https://docs.docker.com/engine/install/)
* [Python3](https://www.python.org/downloads/)
  * argparse
  * configparser
  * json
  * os
  * requests
  * sys
  * time
  * [docker](https://pypi.org/project/docker/) -  Python tool to deploy & clean docker images, volumes and containers (Optional) 
  * [geocoder](https://pypi.org/project/geocoder/) - Python tool to get location (Optional) 
 
Except for optional packages, all required Python packages used tend to be standard. However, in case of an 
issue, installment can be done via [pip3](https://www.activestate.com/resources/quick-reads/how-to-install-and-use-pip3/#:~:text=1%20Open%20the%20Control%20Panel%20and%20navigate%20to,and%20add%20the%20directory%20where%20pip3%20is%20installed%2C)  

```bash
pip3 install ${PACKAGE_NAME}
```


## Builds
* **Debian** runs _Ubuntu:18.04_ and is roughly 287.25MB 
* **Alpine** runs _Alpine:3.7_ and is roughly 56.11MB  

### Latest builds
* **debian** - Stable build using Ubuntu 18.04 operating system for amd64 and arm v7 architecture type
* **debian-arm64** - Stable build using Ubuntu 18.04 operating system for arm64 architecture type
* **alpine** - Stable build using Alpine 3.7 operating system for amd64 and arm v7 architecture type
* **alpine-arm64** - Stable  build using Alpine 3.7 operating system for arm64 architecture type
* **predevelop**_ - Beta build using Ubuntu 18.04 operating system for amd64 and arm v7  architecture type
* **predevelop-arm64** - Beta build using Ubuntu 18.04 operating system for arm64 architecture type
* **predevelop-alpine** - Beta build using Alpine 3.7 operating system for amd64 and arm v7  architecture type
* **predevelop-alpine-arm64** - Beta build using Alpine 3.7 operating system for arm64 architecture type*
 
**Note**: _Alpine_ based builds do not support certain AnyLog functions such as machine insight generated by using [psutil](https://pypi.org/project/psutil/)

 
## Steps 
0. [Contact us](mailto:info@anylog.co) for a password to download AnyLog from docker


1. Clone AnyLog-API: `git clone https://github/AnyLog-co/AnyLog-API`


2. Copy the [sample config](config/config.ini) to a new file & update the parameters as needed for your deployment.   


3. Deploy Postgres, Grafana and AnyLog containers, as well as configuring AnyLog via REST with an MQTT client file included. 
A full list of options available for `main.py` can be found [here](Anylog_API_Options.md).     
```bash
python3 $HOME/AnyLog-API/deployment/main.py ${REST_IP}:${REST_PORT} $HOME/AnyLog-API/config/new_config.ini -e \ 
    --anylog \  
    --psql \  
    --grafana \
    --deployment-file $HOME/my_mqtt_client.al 
```

**Attach to Docker**: `docker attach --detach-keys="ctrl-d"  ${CONTAINER_NAME}`

**Detach from Docker**: `CTRL+d`

4. Stop AnyLog, Postgres and Grafana but don't clean anything
```bash
python3 $HOME/AnyLog-API/deployment/main.py ${REST_IP}:${REST_PORT} $HOME/AnyLog-API/config/new_config.ini -e \
    --disconnect-anylog \
    --disconnect-psql \ 
    --disconnect-grafana 
```

 