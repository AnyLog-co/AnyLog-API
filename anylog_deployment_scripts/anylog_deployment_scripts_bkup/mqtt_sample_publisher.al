# Based on AnyLog's documentation, the following is an example of pushing data into MQTT with AnyLog 
# URL: https://github.com/AnyLog-co/documentation/blob/master/mqtt.md 

message = {
    "value":210,
    "ts":1607959427550,
    "protocol":"modbus",
    "measurement":"temp02",
    "metadata":{
        "company": "test-company", 
        "machine_name":"cutter 23",
        "serial_number":"1234567890"
    }
}

mqtt publish where broker=!mqtt_broker and port=!mqtt_port and user=!mqtt_user and password=!mqtt_password and topic=!mqtt_topic and message = !message

