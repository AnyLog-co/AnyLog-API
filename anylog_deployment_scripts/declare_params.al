#----------------------------------------------------------------------
# The following allows a user to update params prior to starting AnyLog
# If params are not updated then the program uses the default values 
# Please note a user can utilize env params as values by using '$ENV-NAME'
#
# The following examples use default values 
#-------------------------------------------------------------------------
# process !anylog_path/AnyLog-Network/anylog_deployment_scripts/declare_params.al

on error ignore 

# -- General info --  

# Declare public key of the node. 
node_id = get node id 
if not !node_id then
do id create keys for node where password = anylog 
do node_id = get node id 



# Node hostname
hostname = get hostname

# Type of node AnyLog should run
# --> none - an AnyLog instance without anything running.
# --> master - a "notary" system between other nodes in the network via either a public or private blockchain
# --> operator - nodes containing generated by sensors. these can be either physical devices (ex. cars) or remote cloud
# --> publisher - nodes that simply generate data and send them to operator nodes"
# --> query - nodes dedicated to query and BI activity
node_type=$NODE_TYPE

# Name of the anylog instance
node_name=$NODE_NAME

# Operator Member ID - if not set AnyLog will create a new ID 
#member_id=$MEMBER_ID 

# Set company name for node 
company_name=$COMPANY_NAME

# Machine location - coordinates location is accessible via Grafana Map visualization
loc=$LOCATION 

# -- Authentication -- 
set_authentication = $SET_AUTHENTICATION
authentication_user=$AUTHENTICATION_USER 
authentication_passwd=$AUTHENTICATION_PASSWD

# -- Networking -- 
# Master node config 
master_node =  $MASTER_NODE

# TCP port for node used to communicate with other nodes in the network. Please make sure the port is open and avilable
anylog_server_port = $ANYLOG_TCP_PORT 

# REST port for node used to communicate with other nodes in the network. Please make sure the port is open and avilable
anylog_rest_port   = $ANYLOG_REST_PORT 

# Whether to run local MQTT broker 
local_broker = $LOCAL_BROKER

# MQTT broker port 
anylog_broker_port = $ANYLOG_BROKER_PORT 

# -- directory system -- 
#rest_dir    = $DATA_DIR/rest        # dir where data (for storing) is recieved via rest 
#prep_dir    = $DATA_DIR/prep        # dir where data is prepared  
#watch_dir   = $DATA_DIR/watch       # dir for data ready to be stored in operator(s) 
#archive_dir = $DATA_DIR/archive_dir # dir for archive data (ie data sent to other operators) 
#distr_dir   = $DATA_DIR/distr       # distribution ddata dir (ie data coming in from other operators) 
#bkup_dir    = $DATA_DIR/bkup        # dir containing bkup of stored data 
#err_dir     = $DATA_DIR/error       # dir containing data that failed 
#dbms_dir    = $DATA_DIR/dbms        # SQLite database dir 
#blockchain_dir  = $BLOCKCHAIN_DIR                  # blockchain directory 
#blockchain_file = $BLOCKCHAIN_DIR/blockchain.json  # file used for `blockchain get` 
#blockchain_new  = $BLOCKCHAIN_DIR/blockchain.new   
#blockchain_old  = $BLOCKCHAIN_DIR/blockchain.old 

# -- Cluster/Table (operator only) -- 
if $NODE_TYPE == "operator" then 
do member_id = $MEMBER_ID
do enable_cluster = $ENABLE_CLUSTER #s et operator as part of a cluster (True) or not (False)
do if !enable_cluster == True then 
do cluster_id = $CLUSTER_ID
do cluster_name=$CLUSTER_NAME # Name of the cluster
table=$TABLE # list of tables


# Type of database to be used by the AnyLog node
db_type = $DB_TYPE 

# Database credentials -- ${db_user}@{db_ip}:${db_user_password}
db_user = $DB_USER  

# Database access port
db_port = $DB_PORT 

# Logical database name within operator node 
if $NODE_TYPE == "operator" then default_dbms = $DEFAULT_DBMS

# -- MQTT -- 

# Decide whether to enable MQTT
mqtt_enable = $MQTT_ENABLE

# If enabled, code utilizes the same config for MQTT to extract all (other) topics from the broker as raw data
mqtt_enable_other = $MQTT_ENABLE_OTHER 

# MQTT decide if to store data formatted or raw
mqtt_raw_data=$MQTT_RAW_DATA 

# MQTT user from credentials 
mqtt_user = $MQTT_USER
if not !mqtt_user then mqtt_user = '' 

# MQTT password from credentials
mqtt_password = $MQTT_PASSWORD 
if not !mqtt_password then !mqtt_password = '' 

# MQTT broker from credentials 
mqtt_broker = $MQTT_BROKER

# Broker port number
mqtt_broker_port = $MQTT_BROKER_PORT 

# Broker log message - If True, enable internal MQTT debug mode
mqtt_log = $MQTT_LOG 

# MQTT topic to get data from
mqtt_topic_name = $MQTT_TOPIC_NAME

# MQTT database name for topic
mqtt_topic_dbms = $MQTT_TOPIC_DBMS 

# MQTT table name for topic
mqtt_topic_table = $MQTT_TOPIC_TABLE 

# Timestamp value from MQTT object
mqtt_column_timestamp = $MQTT_COLUMN_TIMESTAMP 

# MQTT 'value' column type support - ['str', 'int', 'timestamp', 'bool'],
mqtt_column_value_type=$MQTT_COLUMN_VALUE_TYPE

# Value value from MQTT object
mqtt_column_value = $MQTT_COLUMN_VALUE 

# MQTT columns othen than 'value' and 'timestamp' 
mqtt_extra_columns=$MQTT_EXTRA_COLUMNS 


