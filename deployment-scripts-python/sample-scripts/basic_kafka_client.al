#--------------------------------------------------------------------------------------------------------------#
# (basic) Kafka process based on configuration
# By default, the Message client params (in set_params.al) are based rand data coming into AnyLog's
# Kafka publisher
#--------------------------------------------------------------------------------------------------------------#
# process !local_scripts/demo-scripts/basic_kafka_client.al

on error ignore

:set-params:
kafka_broker = 139.144.46.246
kafka_port = 9092
kafka_reset_value = latest

:run-kafka:
on error call kafka-error
<run kafka consumer where ip=!kafka_broker and port=!kafka_port and topic = (
    name=!msg_topic and
    dbms=!msg_dbms and
    table=!msg_table and
    column.timestamp.timestamp=!msg_timestamp_column and
    column.value=(type=!msg_value_column_type and value=!msg_value_column)
)>

:end-script:
end script

:kafka-error:
echo "Failed to run Kafka consumer:
goto end-script

