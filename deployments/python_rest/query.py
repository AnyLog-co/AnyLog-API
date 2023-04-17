from anylog_connector import AnyLogConnector
import database_deployment
import blockchain_calls
import blockchain_support
from deployment_support import  node_location
import database_calls

def deploy_node(anylog_conn:AnyLogConnector, configuration:dict, exception:bool=False):
    """
    Deploy query node
    :process:
        1. create system_query
        4. create policy if DNE
    :args:
        anylog_conn:AnyLogConnector - Connection via REST
        configuration:dict - node configurations
        exception:bool - wheher to print exceptions
    :params:
        node_type:str - Node type
        node_name:str - Node name
        company:str - company name
        where_conditions:str where conditions
        location, country, state, city - location
        policy:str - generated policy
    """
    node_type = 'master'
    node_name = None
    company = None

    if 'node_name' in configuration:
        node_name = configuration['node_name']
    if 'company_name' in configuration:
        company = configuration['company_name']
        if node_name is None:
            node_name = f"{company.lower().replace(' ', '-')}-{node_type}"

    where_condition = {
        "company": company,
        "name": node_name,
        "ip": configuration['external_ip'],
        "local_ip": configuration['ip'],
        "port": configuration['anylog_server_port'],
        "rest_port": configuration['anylog_rest_port']
    }

    if 'system_query' not in database_calls.get_databases(anylog_conn=anylog_conn, json_format=True, view_help=False,
                                                          exception=exception):
        if 'system_query' in configuration and configuration['system_query'] is True:
            database_deployment.declare_database(anylog_conn=anylog_conn, db_name='system_query',
                                                 anylog_configs=configuration, exception=exception)

    is_policy = blockchain_calls.get_policy(anylog_conn=anylog_conn, policy_type=node_type,
                                            where_conditions=where_condition, bring_conditions=None, bring_values=None,
                                            separator=',', view_help=False, exception=exception)
    if len(is_policy) == 0:
        location, country, state, city = node_location(anylog_conn=anylog_conn, configs=configuration,
                                                       exception=exception)

        policy = blockchain_support.node_policy(policy_type=node_type, name=node_name, company=company,
                                                external_ip=configuration['external_ip'], local_ip=configuration['ip'],
                                                anylog_server_port=configuration['anylog_server_port'],
                                                anylog_rest_port=configuration['anylog_rest_port'],
                                                hostname=configuration['hostname'], member=None, cluster_id=None,
                                                anylog_broker_port=None, location=location, country=country,
                                                state=state,
                                                city=city, exception=True)

        blockchain_calls.post_policy(anylog_conn=anylog_conn, policy=policy, local_publish=True,
                                     ledger_conn=configuration['ledger_conn'], exception=exception)