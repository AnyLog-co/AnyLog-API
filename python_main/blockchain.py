from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.generic_get_calls import get_dictionary
from anylog_api_py.generic_post_calls import execute_config_policy
from anylog_api_py.blockchain_support import generate_blockchain_get, create_config_policy
from anylog_api_py.blockchain_calls import get_policy, prepare_policy, post_policy

def config_policy(anylog_conn:AnyLogConnector, node_configs:dict, exception:bool=False):
    """
    {
        "config": {
            "name": "anylog-node-config",
            "company": "New Company",
            "ip": "'!external_ip'",
            "local_ip": "'!ip'",
            "port": "'!anylog_server_port'",
            "rest_port": "'!anylog_rest_port'",
            "script": [
                "run scheduler 1"
            ]
        }
    }
    """
    policy_name = node_configs['node_name'].lower() + "-config"
    if 'config_policy' in node_configs:
        policy_name = node_configs['config_policy']

    blockchain_stmt = generate_blockchain_get(policy_type='config', where_conditions={'name': policy_name},
                                              bring_values="[*][id]")

    policies = get_policy(anylog_conn=anylog_conn, blockchain_get_cmd=blockchain_stmt)
    if not policies:
        new_policy = create_config_policy(name=policy_name, company=node_configs['company_name'])
        prepare_policy(anylog_conn=anylog_conn, policy=new_policy, view_help=False, exception=exception)
        new_policy = get_dictionary(anylog_conn=anylog_conn, json_format=True, remote_destination=None, view_help=False,
                                    exception=exception)['new_policy']
        post_policy(anylog_conn=anylog_conn, policy=new_policy, ledger_conn=node_configs['ledger_conn'],
                    view_help=False, exception=exception)
        policies = get_policy(anylog_conn=anylog_conn, blockchain_get_cmd=blockchain_stmt)

    execute_config_policy(anylog_conn=anylog_conn, policy_id=policies, view_help=False, exception=exception)




