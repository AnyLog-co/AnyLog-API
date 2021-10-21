# Sample MQTT commands
run mqtt client where broker=rest  and port=2249 and user-agent=anylog and topic = (name=rest and dbms = "bring [dbms]" and table = "bring [table]" and column.timestamp.timestamp = "bring [timestamp]" and column.value.float = "bring [value]")
run mqtt client where broker=local and port=2250 and topic = (name=broker and dbms = "bring [dbms]" and table = "bring [table]" and column.timestamp.timestamp = "bring [timestamp]" and column.value.float = "bring [value]")
