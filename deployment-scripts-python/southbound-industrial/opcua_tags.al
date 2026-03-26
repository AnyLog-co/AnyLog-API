#----------------------------------------------------------------------------------------------------------------------#
# Sample deployment process for OPC-UA
# https://github.com/AnyLog-co/documentation/blob/master/opcua.md
# :steps:
#   1. create OPC-UA policies
#   2. declare policies
#----------------------------------------------------------------------------------------------------------------------#
# process !local_scripts/connectors/opcua_tags.al

:check-vars:
on error ignore
if not !opcua_url then goto missing-opcua-url
if not !opcua_node then goto missing-opcua-node
if not !opcua_frequency then opcua_frequency = 1

:create-policy:
on error goto create-policy-error
<get opcua struct where
    url = !opcua_url and
    node = !opcua_node and
    dbms = !default_dbms and
    format = policy  and
    schema = true and
    class = variable and
    target = "local = true and master = !ledger_conn" and
    output = !tmp_dir/opcua_policies.al>

on error ignore
process !tmp_dir/opcua_policies.al

:opcua-client:
on error ignore
process !local_scripts/connectors/opcua_client.al

:end-script:
end script

:missing-opcua-url:
print "Missing OPC-UA URL cannot declare OPC-UA"
goto end-script

:missing-opcua-node:
print "Missing OPC-UA node ID(s) cannot declare OPC-UA"
goto end-script

:create-policy-error:
print "Failed to create OPC-UA policies"
goto end-script
