#----------------------------------------------------------------------------------------------------------------------#
# Basic initiation of AnyLog Node
# :process:
#   1. set params
#   2. start TCP service
#   3. start REST service
#   4. set license key
#----------------------------------------------------------------------------------------------------------------------#
# process AnyLog-API/deploy_anylog/deployment_script.al

:set-params:
anylog_server_port = 32548
anylog_rest_port = 32549 
license_key = 4df552a98c6d7dbb178e828fd6947b1f3fee9911e03f37fe2106160465d9edba9eb34ca5b0c6b28a2e036dd5ed4c1590d9ae74a099ff1208775e3f3de67e571058a0a2b816e7fc45e06f33cf250851ebbce80e8b60dab00da5c425941637e636285e6883ba299d7ac810411197e09e857ba906ef39ef2cd40910f019a3c44acf2023-12-01bGuest

:tcp-service:
on error call tcp-service-error
<run tcp server where 
    external_ip=!external_ip and external_port=!anylog_server_port and
    internal_ip=!ip and internal_port=!anylog_server_port and
    bind=false and threads=3>

:rest-service;
on error call rest-service-error
<run rest server where 
    external_ip=!external_ip and external_port=!anylog_rest_port and
    internal_ip=!ip and internal_port=!anylog_rest_port and
    bind=false and threads=6>

:set-license:
on error call set-license-error
set license where activation_key=!license_key

:end-script:
get processes
end script

:tcp-service-error:
print "Failed to start TCP service on node"
return

:rest-service-error:
print "Failed to start REST service on node"
return

:set-license-error:
print "Failed to set license key on node"
return