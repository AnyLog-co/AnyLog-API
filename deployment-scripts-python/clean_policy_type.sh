#!/bin/bash
CONN=$1
POLICY=$2

IDS=$(curl -X GET ${CONN} \
  -H "command: blockchain get ${POLICY} bring [*][id] separator=," \
  -H "User-Agent: AnyLog/1.23")


for ID in $(echo ${IDS} | tr ',' ' '); do
  curl -X POST ${CONN} \
    -H "command: run client (!ledger_conn) blockchain drop policy where id=${ID}"
done
