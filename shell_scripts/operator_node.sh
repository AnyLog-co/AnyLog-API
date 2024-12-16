#!/bin/bash
export REST_CONN=127.0.0.1:32349
export LEDGER_CONN=127.0.0.1:32048

# extract key information
anylog_dictionary=$(curl -X GET {$REST_CONN} \
  -H "command: get dictionary where format=json" \
  -H "User-Agent: AnyLog/1.23")

for key in node_name external_ip ip anylog_rest_port anylog_server_port ; do
  export ${key}=$(echo "$anylog_dictionary" | jq -r ".${key}")
done

cluster_id=$(curl -X GET ${REST_CONN} \
  -H "command: blockchain get cluster where name=new_cluster bring.first [*][id]" \
  -H "User-Agent: AnyLog/1.23")

if not ${cluster_id} ; then
  export new_policy='<new_policy={"cluster": {
   "name": "new_cluster",
   "company": "AnyLog"
}}>'

curl -X POST \
  "http://${REST_CONN}" \
  -H "command: blockchain push !new_policy" \
  -H "User-Agent: AnyLog/1.23" \
  -H "destination: ${LEDGER_CONN}" \
  --connect-timeout 30 \
  -d "${new_policy}"
fi

cluster_id=$(curl -X GET ${REST_CONN} \
  -H "command: blockchain get cluster where name=new_cluster bring.first [*][id]" \
  -H "User-Agent: AnyLog/1.23")

operator_id=$(curl -X GET ${REST_CONN} \
  -H "command: blockchain get operator where name=my_operator bring.first [*][id]" \
  -H "User-Agent: AnyLog/1.23")

if not ${operator_id} ; then
  export new_policy='{"operator": {
   "name": ${node_name},
   "company": "AnyLog",
   "ip": ${external_ip},
   "local_ip": ${ip},
   "port": ${anylog_server_port}.int,
   "rest_port": ${anylog_rest_port}.int,
   "cluster": ${cluster_id}
}}>'
curl -X POST \
  "http://${REST_CONN}" \
  -H "command: blockchain push !new_policy" \
  -H "User-Agent: AnyLog/1.23" \
  -H "destination: ${LEDGER_CONN}" \
  --connect-timeout 30 \
  -d "${new_policy}"
done

operator_id=$(curl -X GET ${REST_CONN} \
  -H "command: blockchain get operator where name=my_operator bring.first [*][id]" \
  -H "User-Agent: AnyLog/1.23")

if !enable_partitions == true ; then
  curl -X POST \
    "http://${REST_CONN}" \
    -H "command: partition !default_dbms !table_name using !partition_column by !partition_interval" \
    -H "User-Agent: AnyLog/1.23"

  curl -X POST \
    "http://${REST_CONN}" \
    -H 'command: schedule time=1 day and name="Drop Partitions" task drop partition where dbms=!default_dbms and table=* and keep=3' \
    -H "User-Agent: AnyLog/1.23"
fi

curl -X POST \
  "http://${REST_CONN}" \
  -H 'command: run blobs archiver where dbms=false and folder=true and compress=true and reuse_blobs=true' \
  -H "User-Agent: AnyLog/1.23"

curl -X POST \
  "http://${REST_CONN}" \
  -H 'command: run operator where create_table=true and update_tsd_info=true and compress_json=true and compress_sql=true and archive_json=true and archive_sql=true and blockchain=master and policy=!operator_id and threads=3' \
  -H "User-Agent: AnyLog/1.23"
  >

