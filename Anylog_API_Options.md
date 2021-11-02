The following is a full list of options when running AnyLog-API.       
```
anylog-vm:AnyLog-API orishadmon$ python3 ~/AnyLog-API/deployment/main.py --help 
usage: main.py [-h] [--docker-password DOCKER_PASSWORD] [--docker-only [DOCKER_ONLY]] [--full-deployment [FULL_DEPLOYMENT]] 
               [--anylog [ANYLOG]] [--psql [PSQL]] [--grafana [GRAFANA]] [--update-anylog [UPDATE_ANYLOG]] [--full-clean [FULL_CLEAN]]
               [--disconnect-anylog [DISCONNECT_ANYLOG]] [--rm-policy [RM_POLICY]] [--rm-data [RM_DATA]] [--anylog-rm-volume [ANYLOG_RM_VOLUME]] 
               [--anylog-rm-image [ANYLOG_RM_IMAGE]] [--disconnect-psql [DISCONNECT_PSQL]] [--psql-rm-volume [PSQL_RM_VOLUME]] 
               [--psql-rm-image [PSQL_RM_IMAGE]] [--disconnect-grafana [DISCONNECT_GRAFANA]] [--grafana-rm-volume [GRAFANA_RM_VOLUME]] 
               [--grafana-rm-image [GRAFANA_RM_IMAGE]] [-t TIMEOUT] [-c [UPLOAD_CONFIG]] [-dl [DISABLE_LOCATION]] [-df DEPLOYMENT_FILE] [-e [EXCEPTION]]
               rest_conn config_file

Send REST requests to configure an AnyLog instance.

positional arguments:
  rest_conn             REST connection information
  config_file           AnyLog INI config file

optional arguments:
  -h, --help                                    show this help message and exit
  --docker-password       DOCKER_PASSWORD         password for docker to download/update AnyLog (default: None)
  --docker-only           DOCKER_ONLY             If set, code will not continue once docker instances are up (default: False)
  
  --full-deployment       FULL_DEPLOYMENT         Update & connect to AnyLog, PSQL and Grafana containers (default: False)
  --anylog                ANYLOG                  deploy AnyLog docker container (default: False)
  --psql                  PSQL                    deploy postgres docker container if db type is `psql` in config (default: False)
  --grafana               GRAFANA                 deploy Grafana if `query` in node_type (default: False)
  --update-anylog         UPDATE_ANYLOG           Update AnyLog build (default: False)
  
  --full-clean            FULL_CLEAN              Remove everything AnyLog related from machine (default: False)
  --disconnect-anylog     DISCONNECT_ANYLOG       stop AnyLog docker instance (default: False)
  --rm-policy             RM_POLICY               remove policy from ledger that's not of type 'cluster' or 'table' correlated to the node (default: False)
  --rm-data               RM_DATA                 remove data from database in the correlated attached node (default: False)
  --anylog-rm-volume      ANYLOG_RM_VOLUME        remove AnyLog volumes correlated to the attached node (default: False)
  --anylog-rm-image       ANYLOG_RM_IMAGE         remove AnyLog image (default: False)
  --disconnect-psql       DISCONNECT_PSQL         stop Postgres docker instance (default: False)
  --psql-rm-volume        PSQL_RM_VOLUME          remove Postgres volume (default: False)
  --psql-rm-image         PSQL_RM_IMAGE           remove AnyLog volumes correlated to the attached node (default: False)
  --disconnect-grafana    DISCONNECT_GRAFANA      stop Grafana docker instance (default: False)
  --grafana-rm-volume     GRAFANA_RM_VOLUME       remove Grafana volumes (default: False)
  --grafana-rm-image      GRAFANA_RM_IMAGE        remove Grafana image (default: False)
  
  -t, --timeout           TIMEOUT                 REST timeout period (default: 30)
  -c, --upload-config     UPLOAD_CONFIG           Update information from config_file into AnyLog dictionary (default: False)
  -dl, --disable-location DISABLE_LOCATION        Whether to disable location when adding a new node policy to the ledger (default: False)
  -df, --deployment-file  DEPLOYMENT_FILE         An AnyLog file user would like to deploy in addition to the configurations (default: None)
  -e, --exception         EXCEPTION               print exception errors (default: False)
```