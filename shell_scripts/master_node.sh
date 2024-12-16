#!/bin/bash
export REST_CONN=127.0.0.1:32049
export LEDGER_CONN=127.0.0.1:32048

curl -X POST ${REST_CONN} \
  -H "command: connect dbms blockchain where type=sqlite" \
  -H "User-Agent: AnyLog/1.23"

curl -X POST ${REST_CONN} \
  -H "command: create table ledger where dbms=blockchain" \
  -H "User-Agent: AnyLog/1.23"


curl -X POST ${REST_CONN} \
  -H "command: run blockchain sync where source=master and time=30 seconds and dest=file and connection=${LEDGER_CONN}" \
  -H "User-Agent: AnyLog/1.23"
