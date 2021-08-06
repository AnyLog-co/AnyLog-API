#!/bin/bash 
if [[ $# -eq 1 ]] 
then 
   ROOT_DIR=${1:-$HOME/AnyLog-API} 
else 
   echo "Missing: Path for anylog-deployment & node type(s)" 
   exit 1
fi

mkdir ${ROOT_DIR}/tmp_config

printf "Welcome to AnyLog!\n"
printf "\nThe following can deploy"
printf "\n\tnone - deploy an empty AnyLog instance" 
printf "\n\tfull - deploy complete setup (master, operator, publisher and query)"
printf "\n\tcluster - deploy a cluster (operator, publisher and query)"
printf "\n\tnode - by specifying 'node', you can specify a specific node"
printf "\n\tconfig - deploy a specific config\n" 
read -p "Deployment Type [default: full]: " DEPLOYMENT_TYPE
DEPLOYMENT_TYPE=${DEPLOYMENT_TYPE:-"full"} 
while [[ ! ${DEPLOYMENT_TYPE} == "full" ]] && [[ ! ${DEPLOYMENT_TYPE} == "none" ]] && [[ ! ${DEPLOYMENT_TYPE} == "cluster" ]] && [[ ! ${DEPLOYMENT_TYPE} == "node" ]] && [[ ! ${DEPLOYMENT_TYPE} == "config" ]] 
do
    read -p "Invalid Deployment Type: ${DEPLOYMENT_TYPE}. Deployment Type [default: full]: " DEPLOYMENT_TYPE
    DEPLOYMENT_TYPE=${DEPLOYMENT_TYPE:-"full"}  
done 


if [[ ${DEPLOYMENT_TYPE} == "node" ]] 
then 
   printf "Type of node AnyLog user can run:\n"
   printf "\tmaster - a 'notary' system between other nodes in the network via either a public or private blockchain\n"
   printf "\toperator - nodes containing generated by sensors. these can be either physical devices (ex. cars) or remote cloud\n"
   printf "\tpublisher - nodes that simply generate data and send them to operator nodes\n"
   printf "\tquery - nodes dedicated to query and BI activity\n"
   read -p "Node Type [default: operator | options: master, operator, publisher, query]: " NODE_TYPE
   NODE_TYPE=${NODE_TYPE:-"operator"} 
   while [[ ! ${NODE_TYPE} == "master" ]] && [[ ! ${NODE_TYPE} == "operator" ]] && [[ ! ${NODE_TYPE} == "publisher" ]] && [[ ! ${NODE_TYPE} == "query" ]] 
   do 
      read -p "Invalid Node Type: ${NODE_TYPE}. Node Type [default: operator | options: master, operator, publisher, query]: " NODE_TYPE
      NODE_TYPE=${NODE_TYPE:-"operator"} 
   done 
   NODE_TYPES=(${NODE_TYPE})
elif [[ ${DEPLOYMNET_TYPE} == "cluster" ]] 
then
   NODE_TYPES=(operator publisher query) 
elif [[ ${DEPLOYMENT_TYPE} == "full" ]] 
then
   NODE_TYPES=(master operator publisher query) 
fi 

# <--- Generic params ---> 

# The name of the company correlated with the cluster
read -p "Company Name [default: anylog]: " COMPANY_NAME
COMPANY_NAME=${COMPANY_NAME:-"anylog"} 

FORMAT_COMPANY_NAME=${COMPANY_NAME/ /-}
FORMAT_COMANY_NAME=${FORMAT_COMAPNY_NAME,,} 
DB_FORMAT_COMPANY_NAME=${COMPANY_NAME/ /_}
DB_FORMAT_COMAPNY_NAME=${DB_FORMAT_COMAPNY_NAME,,} 
LOCAL_IP=`curl -X GET ifconfig.me 2> /dev/null`

read -p "Master Node IP+Port [default: ${LOCAL_IP}:2048]: " MASTER_NODE
MASTER_NODE=${MASTER_NODE:-"${LOCAL_IP}:2048"} 

for NODE_TYPE in ${NODE_TYPES[@]} 
do 
   printf "\t--- Set Up for ${NODE_TYPE^} Node ---\n"  
   read -p "Build Type [default: debian | options: alpine, centos, debian]: " BUILD_TYPE
   BUILD_TYPE=${BUILD_TYPE:-"debian"} 
    
   # Machine location - coordinates location is accessible via Grafana Map visualization
   read -p "Device Location [default: empty | if empty, will use coordiantes]: " LOCATION 
   LOCATION=${LOCATION} 
   
   TMP_NODE_NAME=${COMPANY_NAME/ /-}-${NODE_TYPE}
   read -p "Node Name [defult: ${TMP_NODE_NAME}]: " NODE_NAME
   NODE_NAME=${NODE_NAME:-"${TMP_NODE_NAME}"} 

   read -p "Enable REST authentication [default: false]: " SET_AUTHENTICATION
   SET_AUTHENTICATION=${SET_AUTHENTICATION:-"false"} 
   while [[ ! ${SET_AUTHENTICATION} == "false" ]] && [[ ! ${SET_AUTHENTICATION} == "true" ]] 
   do
      read -p "Invalid option: ${SET_AUTHENTICATION}. Enable REST authentication [default: false]: " SET_AUTHENTICATION
      SET_AUTHENTICATION=${SET_AUTHENTICATION:-"false"}
   done  

   if [[ ${SET_AUTHENTICATION} == "true" ]]
   then
      read -p "Username & Password [default ${FORMAT_COMPANY_NAME}:${FORMAT_COMPANY_NAME}]: " AUTHENTICATION_USER_INFO
      AUTHENTICATION_USER_INFO=${AUTHENTICATION_USER_INFO:-${FORMAT_COMPANY_NAME}:${FORMAT_COMPANY_NAME}}
   fi 
   CONFIG_FILE=${ROOT_DIR}/tmp_config/${NODE_NAME}.ini 
   cp ${ROOT_DIR}/support/config/config.ini ${CONFIG_FILE} 

   sed -i "s/build_type=<build_type>/build_type=${BUILD_TYPE}/g" ${CONFIG_FILE} 
   sed -i "s/node_type=<node_type>/node_type=${NODE_TYPE}/g" ${CONFIG_FILE} 
   sed -i "s/node_name=<node_name>/node_name=${NODE_NAME}/g" ${CONFIG_FILE} 
   sed -i "s/company_name=<company_name>/company_name=${COMPANY_NAME}/g" ${CONFIG_FILE} 
   sed -i "s/set_authentication=<set_authentication>/set_authentication=${SET_AUTHENTICATION}/g" ${CONFIG_FILE}

   if [[ ! -z ${LOCATION} ]] ; then sed -i "s/#location=<location>/location=${LOCATION}/g" ${CONFIG_FILE} ; fi 
   if [[ ! -z ${MEMBER_ID} ]] ; then sed -i "s/#member_id=<member_id>/member_id=${MEMBER_ID}/g" ${CONFIG_FILE} ; fi 
   if [[ ! -z ${AUTHENTICATION_USER_INFO} ]] 
   then 
       sed -i "s/#authentication_user_info=<authentication_user_info>/authentication_user_info=${AUTHENTICATION_USER_INFO}/g" ${CONFIG_FILE}
   fi 

   # <--- Network params ---> 
   if [[ -z ${TMP_ANYLOG_TCP_PORT} ]]
   then 
      TMP_ANYLOG_TCP_PORT=2048 
   else
      TMP_ANYLOG_TCP_PORT=$(( ${TMP_ANYLOG_TCP_PORT} + 100 )) 
   fi 

   read -p "AnyLog TCP Port [default: ${TMP_ANYLOG_TCP_PORT}]: " ANYLOG_TCP_PORT 
   ANYLOG_TCP_PORT=${ANYLOG_TCP_PORT:-${TMP_ANYLOG_TCP_PORT}}

   TMP_ANYLOG_REST_PORT=$(( ${ANYLOG_TCP_PORT} + 1 ))
   read -p "AnyLog REST Port [default: ${TMP_ANYLOG_REST_PORT}]: " ANYLOG_REST_PORT 
   ANYLOG_REST_PORT=${ANYLOG_REST_PORT:-${TMP_ANYLOG_REST_PORT}}
   
   if [[ ${NODE_TYPE} == "master" ]] && [[ ! ${ANYLOG_TCP_PORT} == 2048 ]] 
   then
      read -p "The original master node config doesn't match the new configs. Would you like to update master (y/n)? " UPDATE_MASTER 
      UPDATE_MASTER=${UPDATE_MASTER:-"y"} 
      while [[ ! ${UPDATE_MASTER} == "y" ]] && [[ ! ${UPDATE_MASTER} == "n" ]] 
      do 
         read -p "Invalid option '${UPDATE_MASTER}'. Would you like to update master (y/n)? " UPDATE_MASTER
	 UPDATE_MASTER=${UPDATE_MASTER:-"y"}
      done
      if [[ ${UPDATE_MASTER} == "y" ]] 
      then
         read -p "Master Node [default: ${LOCAL_IP}:${ANYLOG_TCP_PORT}]: " MASTER_NODE
	 MASTER_NODE=${MASTER_NODE:-${LOCAL_IP}:${ANYLOG_TCP_PORT}}
      fi 
   fi    
   if [[ ${NODE_TYPE} == "publisher" ]] || [[ ${NODE_TYPE} == "operator" ]]
   then
      read -p "Enable Local Broker [default: false]: " LOCAL_BROKER
      LOCAL_BROKER=${LOCAL_BROKER:-"false"} 
      while [[ ! ${LOCAL_BROKER} == "true" ]] && [[ ! ${LOCAL_BROKER} == "false" ]] 
      do 
          read -p "Invalid option: ${LOCAL_BROKER}. Enable Local Broker [default: false]: " LOCAL_BROKER
	  LOCAL_BROKER=${LOCAL_BROKER:-"false"} 
       done 
       if [[ ${LOCAL_BROKER} == "true" ]] 
       then
	  TMP_ANYLOG_BROKER_PORT=$(( ${ANYLOG_REST_PORT} + 1))
          read -p "Broker Port [default: ${TMP_ANYLOG_BROKER_PORT}]: " ANYLOG_BROKER_PORT 
	  ANYLOG_BROKER_PORT=${ANYLOG_BROKER_PORT:-${TMP_ANYLOG_BROKER_PORT}} 
       fi 
   fi 
   sed -i "s/master_node=<master_node>/master_node=${MASTER_NODE}/g" ${CONFIG_FILE}
   sed -i "s/anylog_tcp_port=<anylog_tcp_port>/anylog_tcp_port=${ANYLOG_TCP_PORT}/g" ${CONFIG_FILE}
   sed -i "s/anylog_rest_port=<anylog_rest_port>/anylog_rest_port=${ANYLOG_REST_PORT}/g" ${CONFIG_FILE}

   if [[ ! -z ${LOCAL_BROKER} ]]       ; then sed -i "s/#local_broker=<local_broker>/local_broker=${LOCAL_BROKER}/g" ${CONFIG_FILE} 			 ; fi 
   if [[ ! -z ${ANYLOG_BROKER_PORT} ]] ; then sed -i "s/#anylog_broker_port=<anylog_broker_port>/anylog_broker_port=${ANYLOG_BROKER_PORT}/g" ${CONFIG_FILE} ; fi 

   # Database 
   DB_TYPE=sqlite
   DB_USER=${DB_FORMAT_COMPANY_NAME}@127.0.0.1:${DB_FORMAT_COMPANY_NAME}
   DB_PORT=5432

   if [[ ! ${DB_TYPE} == "alpine" ]] 
   then
      read -p "DB Type [default: psql | options: psql, sqlite]: " DB_TYPE
      DB_TYPE=${DB_TYPE:-"psql"} 
      while [[ ! ${DB_TYPE} == "psql" ]] && [[ ! ${DB_TYPE} == "sqlite" ]] 
      do
         read -p "Invalid DB Type: ${DB_TYPE}. DB Type [default: psql | options: psql, sqlite]: " DB_TYPE 
	 DB_TYPE=${DB_TYPE:-"psql"} 
      done 
      if [[ ! ${DB_TYPE} == "sqlite" ]] 
      then
         read -p "DB User [default: ${DB_FORMAT_COMPANY_NAME}@127.0.0.1:${DB_FORMAT_COMPANY_NAME} | format: username@db_ip:password]: " DB_USER 
         DB_USER=${DB_USER:-${DB_FORMAT_COMPANY_NAME}@127.0.0.1:${DB_FORMAT_COMPANY_NAME}} 

         if [[ ${DB_TYPE} == "psql" ]] 
         then
            read -p "DB Port [default: 5432]: " DB_PORT 
	    DB_PORT=${DB_PORT:-5432} 
         fi 
      fi 
   fi 
   sed -i "s/db_type=<db_type>/db_type=${DB_TYPE}/g" ${CONFIG_FILE}
   sed -i "s/db_user=<db_user>/db_user=${DB_USER}/g" ${CONFIG_FILE}
   sed -i "s/db_port=<db_port>/db_port=${DB_PORT}/g" ${CONFIG_FILE}

   # Operator specific params 
   if [[ ${NODE_TYPE} == "operator" ]] 
   then
      read -p "Default Database Name [default: ${DB_FORMAT_COMPANY_NAME}]: " DEFAULT_DBMS
      DEFAULT_DBMS=${DEFAULT_DBMS:-"${DB_FORMAT_COMPANY_NAME}"}

      read -p "AnyLog Operator Member ID [If not set AnyLog will generate a new number]: " MEMBER_ID 
      MEMBER_ID=${MEMBER_ID} 

      read -p "Enable Cluster [default: true]: " ENABLE_CLUSTER
      ENABLE_CLUSTER=${ENABLE_CLUSTER:-"true"} 
      while [[ ! ${ENABLE_CLUSTER} == "false" ]] && [[ ! ${ENABLE_CLUSTER} == "true" ]] 
      do
         read -p "Invalid Option: ${ENABLE_CLUSTER}. Enable Cluster [default: false]: " ENABLE_CLUSTER 
	 ENABLE_CLUSTER=${ENABLE_CLUSTER:-"true"} 
      done 

      if [[ ${ENABLE_CLUSTER} == "true" ]] 
      then
	 read -p "Create a new cluster [default: true]: " NEW_CLUSTER 
	 NEW_CLUSTER=${NEW_CLUSTER:-"true"} 
	 while [[ ! ${NEW_CLUSTER} == "true" ]] && [[ ! ${NEW_CLUSTER} == "false" ]]
	 do
            read -p "Invalid option: ${NEW_CLUSTER}. Create a new cluster [default: true]: " NEW_CLUSTER 
	    NEW_CLUSTER=${NEW_CLUSTER:-"true"}
	 done 
	 if [[ ${NEW_CLUSTER} == "false" ]] 
         then 
            read -p "Cluster ID [leave empty if you'd like to create a new cluster]: " CLUSTER_ID
	    CLUSTER_ID=${CLUSTER_ID} 
	 else 
            read -p "Cluster Name [default: ${FORMAT_COMPANY_NAME}-new-cluster]: " CLUSTER_NAME
	    CLUSTER_NAME=${CLUSTER_NAME:-"${FORMAT_COMPANY_NAME}-new-cluster"} 
	 fi 
      fi 
      if [[ ${NEW_CLUSTER} == "true" ]] || [[ -z ${NEW_CLUSTER} ]]  
      then 
         read -p "Comma Seperated List of Tables: " TABLE
         TABLE=${TABLE}
      fi 
      read -p "Database Name [default: ${DEFAULT_DBMS}]: " DB_NAME
      DB_NAME=${DB_NAME:-${DEFAULT_DBMS}}

      sed -i "s/#default_dbms=<db_name>/default_dbms=${DEFAULT_DBMS}/g" ${CONFIG_FILE} 
      sed -i "s/#enable_cluster=<enable_cluster>/enable_cluster=${ENABLE_CLUSTER}/g" ${CONFIG_FILE}  
      if [[ ! -z ${MEMBER_ID} ]] ; then sed -i "s/#member_id=<member_id>/member_id=${MEMBER_ID}/g" ${CONFIG_FILE} ; fi 
      if [[ ${ENABLE_CLUSTER} == "true" ]] && [[ ! -z ${CLUSTER_ID} ]] 
      then
         sed -i "s/#cluster_id=<cluster_id>/cluster_id=${CLUSTER_ID}/g" ${CONFIG_FILE} 
      else 
         sed -i "s/#cluster_name=<cluster_name>/cluster_name=${CLUSTER_NAME}/g" ${CONFIG_FILE} 
      fi 
      if [[ ! -z ${TABLE} ]] ; then sed -i "s/#table=<table>/table=${TABLE}/g" ${CONFIG_FILE} ; fi
   fi   

   # MQTT 
   if [[ ${NODE_TYPE} == "publisher" ]] || [[ ${NODE_TYPE} == "operator" ]] 
   then
      if [[ ${LOCAL_BROKER} == "true" ]] ; then DEFAULT_MQTT="true" ; else DEFAULT_MQTT="false" ; fi 
      read -p "Enable MQTT client [default: ${DEFAULT_MQTT}]: " MQTT_ENABLE
      MQTT_ENABLE=${MQTT_ENABLE:-${DEFAULT_MQTT}} 
      while [[ ! ${MQTT_ENABLE} == "false" ]] && [[ ! ${MQTT_ENABLE} == "true" ]] 
      do
         read -p "Invalid Option: ${MQTT_ENABLE}. Enable MQTT [default: ${DEFAULT_MQTT}]: " MQTT_ENABLE
         MQTT_ENABLE=${MQTT_ENABLE:-${DEFAULT_MQTT}} 
      done 

      read -p "Extract data from other MQTT topics - same connection info [default: false]: " MQTT_ENABLE_OTHER
      MQTT_ENABLE_OTHER=${MQTT_ENABLE_OTHER:-"false"} 
      while [[ ! ${MQTT_ENABLE_OTHER} == "false" ]] && [[ ! ${MQTT_ENABLE_OTHER} == "true" ]] 
      do
         read -p "Invalid Option: ${MQTT_ENABLE_OTHER}. Extract data from other MQTT topics - same connection info [default: false]: " MQTT_ENABLE_OTHER
         MQTT_ENABLE_OTHER=${MQTT_ENABLE_OTHER:-"false"} 
      done 
      sed -i "s/#mqtt_enable=<mqtt_enable>/mqtt_enable=${MQTT_ENABLE}/g" ${CONFIG_FILE}
      sed -i "s/#mqtt_enable_other=<mqtt_enable_other>/mqtt_enable_other=${MQTT_ENABLE_OTHER}/g" ${CONFIG_FILE}
   fi  

   if [[ ${MQTT_ENABLE} == "true" ]] || [[ ${MQTT_ENABLE_OTHER} == "true" ]]
   then
      if [[ ${LOCAL_BROKER} == "true" ]] 
      then 
         read -p "MQTT Connection info [default: local | format: user@broker:password | sample: mqwdtklv@driver.cloudmqtt.com:uRimssLO4dIo]: " MQTT_CONN 
         MQTT_CONN=${MQTT_CONN:-"local"} 

         read -p "MQTT Port [default: ${ANYLOG_BROKER_PORT}]: " MQTT_PORT
         MQTT_PORT=${MQTT_PORT:-${ANYLOG_BROKER_PORT}}
      else
         read -p "MQTT Connection info [default: empty | format: user@broker:password | sample: mqwdtklv@driver.cloudmqtt.com:uRimssLO4dIo]: " MQTT_CONN 
         MQTT_CONN=${MQTT_CONN} 
         while [[ -z ${MQTT_CONN} ]]
         do
            read -p "When MQTT is enabled, connection information cannot be empty. MQTT Connection info [default: empty | format: user@broker:password | sample: mqwdtklv@driver.cloudmqtt.com:uRimssLO4dIo]: " MQTT_CONN 
            MQTT_CONN=${MQTT_CONN} 
         done 
         read -p "MQTT Port [default: empty | suggested: 18975]: " MQTT_PORT
         MQTT_PORT=${MQTT_PORT}
      fi 
 

      read -p "Enable MQTT Logging [default: false]: " MQTT_LOG
      MQTT_LOG=${MQTT_LOG:-"false"}
      while [[ ! ${MQTT_LOG} == "false" ]] && [[ ! ${MQTT_LOG} == "true" ]] 
      do
         read -p "Invalid Option: ${MQTT_LOG}. Enable MQTT Logging [default: false]: " MQTT_LOG
         MQTT_LOG=${MQTT_LOG:-"false"}
      done 
      
      sed -i "s/#mqtt_conn_info=<mqtt_conn_info>/mqtt_conn_info=${MQTT_CONN}/g" ${CONFIG_FILE}
      sed -i "s/#mqtt_broker_port=<mqtt_broker_port>/mqtt_broker_port=${MQTT_PORT}/g" ${CONFIG_FILE}
      sed -i "s/#mqtt_log=<mqtt_log>/mqtt_log=${MQTT_LOG}/g" ${CONFIG_FILE}
   fi 

   if [[ ${MQTT_ENABLE} == "true" ]] 
   then
      bold=$(tput bold)
      normal=$(tput sgr0)
      printf "\n${bold}The following are complex options for extracting MQTT information. If one or more is missing, then data will be stored in generic files.${normal}\n" 

      read -p "MQTT Topic [default: empty | suggested: ${DB_FORMAT_COMPANY_NAME}]: " MQTT_TOPIC 
      MQTT_TOPIC=${MQTT_TOPIC} 

      if [[ -z ${DB_NAME} ]] ; then DB_NAME=${DB_FORMAT_COMPANY_NAME} ; fi 
      read -p "MQTT Database [default: empty | suggested: ${DB_NAME} ]: " MQTT_TOPIC_DBMS 
      MQTT_TOPIC_DBMS=${MQTT_TOPIC_DBMS}

      read -p "MQTT Table Name [default: empty | sample: bring [metadata][machine_name]]: " MQTT_TABLE_NAME 
      MQTT_TABLE_NAME=${MQTT_TABLE_NAME} 

      read -p "MQTT Timestamp Column [default: bring [ts]]: " MQTT_COLUMN_TIMESTAMP
      MQTT_COLUMN_TIMESTAMP=${MQTT_COLUMN_TIMESTAMP} 

      read -p "MQTT Value Column Type [default: empty | options: str, int, timestamp, bool]: " MQTT_COLUMN_VALUE_TYPE
      MQTT_COLUMN_VALUE_TYPE=${MQTT_COLUMN_VALUE_TYPE} 
      if [[ ! -z ${MQTT_COLUMN_VALUE_TYPE} ]] 
      then 
	 # If the value type isnt' empty the default changes to str 
         while [[ ! ${MQTT_COLUMN_VALUE_TYPE} == "str" ]] && [[ ! ${MQTT_COLUMN_VALUE_TYPE} == "int" ]] && [[ ! ${MQTT_COLUMN_VALUE_TYPE} == "timestamp" ]] && [[ ! ${MQTT_COLUMN_VALUE_TYPE} == "bool" ]] 
         do
            read -p "Invalid column type: ${MQTT_COLUMN_VALUE_TYPE}. MQTT Value Column Type [default: str | options: str, int, timestamp, bool]: " MQTT_COLUMN_VALUE_TYPE
            MQTT_COLUMN_VALUE_TYPE=${MQTT_COLUMN_VALUE_TYPE:-"str"}
         done 
      fi 

      read -p "MQTT Value Column [default: none | sample: bring [value]]: " MQTT_COLUMN_VALUE
      MQTT_COLUMN_VALUE=${MQTT_COLUMN_VALUE} 

      read -p "Any other columns to extract from MQTT data [default: empty | sample: and column.new_column.str='and bring [new_column]']: " MQTT_EXTRA_COLUMN 
      MQTT_EXTRA_COLUMN=${MQTT_EXTRA_COLUMN} 

      if [[ ! -z ${MQTT_TOPIC} ]]             ; then sed -i "s/#mqtt_topic_name=<mqtt_topic_name>/mqtt_topic_name=${MQTT_TOPIC}/g"  ${CONFIG_FILE}        		 	     ; fi

      if [[ ! -z ${MQTT_TOPIC_DBMS} ]]        ; then echo "test" ; sed -i "s/#mqtt_topic_dbms=<mqtt_topic_dbms>/mqtt_topic_dbms=${MQTT_TOPIC_DBMS}/g" ${CONFIG_FILE}    		  	     ; fi 
      if [[ ! -z ${MQTT_TABLE_NAME} ]]        ; then sed -i "s/#mqtt_topic_table=<mqtt_topic_table>/mqtt_topic_table=${MQTT_TABLE_NAME}/g" ${CONFIG_FILE} 			     ; fi 
      if [[ ! -z ${MQTT_COLUMN_TIMESTAMP} ]]  ; then sed -i "s/#mqtt_column_timestamp=<mqtt_column_timestamp>/mqtt_column_timestamp=${MQTT_COLUMN_TIMESTAMP}/g" ${CONFIG_FILE}     ; fi
      if [[ ! -z ${MQTT_COLUMN_VALUE_TYPE} ]] ; then sed -i "s/#mqtt_column_value_type=<mqtt_column_value_type>/mqtt_column_value_type=${MQTT_COLUMN_VALUE_TYPE}/g" ${CONFIG_FILE} ; fi  
      if [[ ! -z ${MQTT_COLUMN_VALUE} ]]      ; then sed -i "s/#mqtt_column_value=<mqtt_column_value>/mqtt_column_value=${MQTT_COLUMN_VALUE}/g" ${CONFIG_FILE}                     ; fi  
      if [[ ! -z ${MQTT_EXTRA_COLUMN} ]]  	   ; then sed -i "S/#mqtt_extra_column=<mqtt_extra_column>/mqtt_extra_column=${MQTT_EXTRA_COLUMN}/g" ${CONFIG_FILE} 		     ; fi 
      exit 1 
   fi 
done   

# Deploy Node(s) based on config  
for FILE in `ls ${ROOT_DIR}/tmp_config`
do
   CONFIG_FILE=${ROOT_DIR}/tmp_config/${FILE} 
   mv ${CONFIG_FILE} ${ROOT_DIR}/config
done 
rm -rf ${ROOT_DIR}/tmp_config
