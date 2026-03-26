#-----------------------------------------------------------------------------------------------------------------------
# generic process to declare policy on blockchain (using node key)
#-----------------------------------------------------------------------------------------------------------------------
# process !local_scripts/node-deployment/policies/publish_policy.al
on error ignore
if !debug_mode == true then set debug on

:set-params:
error_code = 0

:private-key:
if !debug_mode == true then print "Check whether authentication is enabled and that private key exists"

if !enable_auth == true and not !node_private_key then
do on error ignore
do node_private_key = get private key where keys_file = !key_name
do if not !node_private_key then goto private-key-error

:prepare-policy:
if !debug_mode == true then print "Prepare new policy with signature if authentication is enabled"

on error goto sign-policy-error
if !enable_auth == true then new_policy = id sign !new_policy where key = !node_private_key and password = !node_password
validate_policy = json !new_policy
if not !validate_policy then goto prepare-policy-error

:declare-policy:
if !debug_mode == true then print "Declare policy on blockchain"

on error call declare-policy-error
blockchain prepare policy !new_policy

if !is_config == true then blockchain insert where policy=!new_policy and local=true
else blockchain insert where policy=!new_policy and local=true and master=!ledger_conn
# else if !node_policy == true and !blockchain_source == master then blockchain insert where policy=!new_policy and local=true and blockchain=optimism
# else blockchain insert where policy=!new_policy and local=true

:end-script:
end script

:private-key-error:
echo "Failed to get private key from generated node key"
goto end-script

:sign-policy-error:
# error code 1 - failed to sign policy
error_code = 1

:prepare-policy-error:
# error code 2 - policy is not in the correct format
error_code = 2

:declare-policy-error:
# error code 3 - failed to publish policy on the blockchain
error_code = 3
