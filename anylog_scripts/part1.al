# The following script (in REST) should be run each time a node started
set anylog home !anylog_root_dir
set authentication off

connect dbms blockchain where type=psql and user = !db_user and password = !db_passwd and ip = !db_ip and port = !db_port

connect dbms almgm where type=psql and user = !db_user and password = !db_passwd and ip = !db_ip and port = !db_port # Init the test dbms (for user data)

connect dbms system_query where type=sqlite

connect dbms !default_dbms where type=psql and user = !db_user and password = !db_passwd and ip = !db_ip and port = !db_port

run scheduler 1

run blockchain sync where source=master and time=!sync_time and dest=file and connection=!master_node

partition !default_dbms * using !partition_column by !partition_interval

schedule time = 1 day and name = "Remove Old Partitions" task drop partition where dbms=!default_dbms and table =!table_name and keep=!partition_keep

set buffer threshold where write_immediate = true

run streamer

run mqtt client where broker=!broker and port=!anylog_rest_port and user-agent=anylog and log=!mqtt_log and topic=(name=!mqtt_topic_name and dbms=!mqtt_topic_dbms and table=!mqtt_topic_table and column.timestamp.timestamp=!mqtt_column_timestamp and column.value=(value=!mqtt_column_value and type=!mqtt_column_value_type))

run operator where create_table=true and update_tsd_info=true and archive=true and distributor=true and master_node=!master_node
