# An example of MQTT client against local REST with a specific topic
# Sample data used: {"dbms": "test", "table": "new_table", "ts": "2021-01-01 00:00:00", "values": 3.14159, "other": "ecca9210-497f-42b6-8d5f-538cb64c8f0e"}
run mqtt client where broker=rest and port=2049 user-agent=python and log=false and topic=(name=anylog-rest and dbms="bring [dbms]" and table="bring [table]" and column.timestamp.timestamp="bring [ts]" and column.value.float="bring [values]" and column.value_id.str="bring [other]")





