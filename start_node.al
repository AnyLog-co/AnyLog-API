#----------------------------------------------------------------------------------------------------------------------#
# Configure networking for using the API tool
#----------------------------------------------------------------------------------------------------------------------#
# process start_node.al

:set-params:
on error ignore
anylog_server_port = 2048
anylog_rest_port = 2049
# anylog_broker_port = 2049

set tcp_bind = false
set rest_bind = false
set broker_bind = false

tcp_threads = 3
rest_threads = 6
broker_threads = 3
rest_timeout = 30

:tcp-networking:
on error goto tcp-networking-error
<run tcp server where
    external_ip=!external_ip and external_port=!anylog_server_port and
    internal_ip=!ip and internal_port=!anylog_server_port and
    bind=!tcp_bind and threads=!tcp_threads>

:rest-networking:
on error goto rest-networking-error
<run rest server where
    external_ip=!external_ip and external_port=!anylog_rest_port and
    internal_ip=!ip and internal_port=!anylog_rest_port and
    bind=!rest_bind and threads=!rest_threads and timeout=!rest_timeout>

if not !anylog_broker_port then goto end-script

:broker-networking:
on error goto broker-networking-error
<run message broker where
    external_ip=!external_ip and external_port=!anylog_broker_port and
    internal_ip=!ip and internal_port=!anylog_broker_port and
    bind=!broker_bind and threads=!broker_threads>

:end-script:
end script

:terminate-scripts:
exit scripts

:tcp-networking-error:
print "Error: Failed to connect to TCP with IP address - unable to continue deployment process"
goto terminate-scripts

:rest-networking-error:
print "Error: Failed to connect to REST with IP address - unable to continue deployment process"
goto terminate-scripts

:broker-networking-error:
print "Error: Failed to connect to Message Broker with IP address - will continue deployment without Message Broker"
do goto terminate-scripts

