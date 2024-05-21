# AnyLog API 

The following package simplifies the accessibility to the AnyLog/EdgeLake API. 

## Requirements 

Either EdgeLake or AnyLog node running with Network REST configuration already preset with desired connection information 
values. Otherwise, API tool will not be able to communicate with the node.  

[Sample Script](start_node.al)
```anylog
:tcp-networking:
<run tcp server where
    external_ip=!external_ip and external_port=!anylog_server_port and
    internal_ip=!overlay_ip and internal_port=!anylog_server_port and
    bind=!tcp_bind and threads=!tcp_threads>

:rest-networking:
<run rest server where
    external_ip=!external_ip and external_port=!anylog_rest_port and
    internal_ip=!ip and internal_port=!anylog_rest_port and
    bind=!rest_bind and threads=!rest_threads and timeout=!rest_timeout>


:broker-networking:
on error goto broker-networking-error
<run message broker where
    external_ip=!external_ip and external_port=!anylog_broker_port and
    internal_ip=!ip and internal_port=!anylog_broker_port and
    bind=!broker_bind and threads=!broker_threads>
```
 


