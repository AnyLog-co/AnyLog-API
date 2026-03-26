#----------------------------------------------------------------------------------------------------------------------#
# Generic call to initiate monitoring database + declare / execute policies
#   1. create database
#   2. declare node monitoring
#   3. create syslog monitoring
#   4. create docker monitoring
#----------------------------------------------------------------------------------------------------------------------#
# process !local_scripts/southbound-monitoring/deploy_monitoring.al

on error ignore
reset error log


if !node_monitoring == false and !syslog_monitoring == false and !docker_monitoring == false then goto end-script

else if !node_type == operator and (!node_monitoring == true or !syslog_monitoring == true or !docker_monitoring == true) then
do process !local_scripts/node-deployment/database/configure_dbms_monitoring.al

if !node_monitoring   == true then process !local_scripts/southbound-monitoring/policy_node_monitoring.al
if !syslog_monitoring == true then process !local_scripts/southbound-monitoring/policy_syslog_monitoring.al
if !docker_monitoring == true then process !local_scripts/southbound-monitoring/policy_docker_monitoring.al

:end-script:
end script