import json

import support
from anylog_connector import AnyLogConnector
import database_deployment
import blockchain_calls
import blockchain_support
from deployment_support import  node_location

def deploy_node(anylog_conn:AnyLogConnector, configuration:dict, exception:bool=False):
    database_deployment.declare_database(anylog_conn=anylog_conn, db_name='blockchain', anylog_configs=configuration, exception=exception)
    database_deployment.declare_table(anylog_conn=anylog_conn, db_name='blockchain', table_name='ledger', exception=exception)
    if 'system_query' in configuration and configuration['system_query'] is True:
        database_deployment.declare_database(anylog_conn=anylog_conn, db_name='system_query', anylog_configs=configuration, exception=exception)

    node_type = 'master'
    node_name = None
    company = None
    location, country, state, city = node_location(anylog_conn=anylog_conn, configs=configuration, exception=exception)

    if 'node_name' in configuration:
        node_name = configuration['node_name']
    if 'company_name' in configuration:
        company = configuration['company_name']
        if node_name is None:
            node_name = f"{company.lower().replace(' ', '-')}-{node_type}"

    policy = blockchain_support.node_policy(policy_type=node_type, name=node_name, company=company,
                                            external_ip=configuration['external_ip'], local_ip=configuration['ip'],
                                            anylog_server_port=configuration['anylog_server_port'],
                                            anylog_rest_port=configuration['anylog_rest_port'],
                                            hostname=configuration['hostname'], member=None, cluster_id=None,
                                            anylog_broker_port=None, location=location, country=country, state=state,
                                            city=city, exception=True)
    print(json.dumps(policy, indent=4))
    # if isinstance(policy, dict):
    #     policy = support.json_dumps(policy, exception=exception)
    # blockchain_calls.post_policy(anylog_conn=anylog_conn, policy=policy, local_publish=True,
    #                              ledger_conn=configuration['ledger_conn'], exception=exception)