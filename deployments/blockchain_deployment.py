import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'python_rest'))

from anylog_connector import AnyLogConnector
import blockchain_calls
import blockchain_support
import generic_get_calls
import find_location


def __build_full_info(anylog_configs)->dict:
    """
    Get where conditions for policy verification
    :args:
        anylog_configs:dict - AnyLog configruations
    :params:
        where_conditions:dict - key/value pairs for `blockchain get` where conditions
    :return:
        where_conditions
    """
    where_conditions = {}
    if 'node_name' in anylog_configs:
        where_conditions['name'] = anylog_configs['node_name']
    if 'company_name' in anylog_configs:
        where_conditions['company'] = anylog_configs['company_name']
    if 'external_ip' in anylog_configs:
        where_conditions['ip'] = anylog_configs['external_ip']
    if 'proxy_ip' in anylog_configs:
        where_conditions['local_ip'] = anylog_configs['proxy_ip']
    elif 'ip' in anylog_configs:
        where_conditions['local_ip'] = anylog_configs['ip']
    if 'anylog_server_port' in anylog_configs:
        where_conditions['port'] = anylog_configs['anylog_server_port']
    if 'anylog_rest_port' in anylog_configs:
        where_conditions['rest_port'] = anylog_configs['anylog_rest_port']

    return where_conditions


def __build_name_info(anylog_configs)->dict:
    """
    Get where conditions for policy verification - specific node and company name
    :args:
        anylog_configs:dict - AnyLog configruations
    :params:
        where_conditions:dict - key/value pairs for `blockchain get` where conditions
    :return:
        where_conditions
    """
    where_conditions = {}
    if 'node_name' in anylog_configs:
        where_conditions['name'] = anylog_configs['node_name']
    if 'company_name' in anylog_configs:
        where_conditions['company'] = anylog_configs['company_name']

    return where_conditions


def __build_network_info(anylog_configs:dict, external:bool=False, rest:bool=False)->dict:
    """
    Get where conditions for policy verification - networking info specific 
    :args:
        anylog_configs:dict - AnyLog configruations
        external;bool - external IP
        rest:bool - REST port
    :params:
        where_conditions:dict - key/value pairs for `blockchain get` where conditions
    :return:
        where_conditions
    """
    where_conditions = {}

    if external is True and 'external_ip' in anylog_configs:
        where_conditions['ip'] = anylog_configs['external_ip']
    elif external is False and 'proxy_ip' in anylog_configs:
        where_conditions['local_ip'] = anylog_configs['proxy_ip']
    elif external is False and 'ip' in anylog_configs:
        where_conditions['local_ip'] = anylog_configs['ip']
    if rest is False and 'anylog_server_port' in anylog_configs:
        where_conditions['port'] = anylog_configs['anylog_server_port']
    elif rest is True and 'anylog_rest_port' in anylog_configs:
        where_conditions['rest_port'] = anylog_configs['anylog_rest_port']

    return where_conditions


def __extract_policy(anylog_conn:AnyLogConnector, exception:bool=False)->str:
    """
    Extract new generated policy
    :args:
        anylog_conns:AnyLogConnector - connection to AnyLog REST
        exception:bool - whether to print exception
    :params:
        policy:str - prepared generated policy as JSON string
        anylog_dict:dict - extracted AnyLog dictionary
    :return:
        policy
    """
    policy = None

    anylog_dict = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, exception=exception)
    if 'new_policy' in anylog_dict:
        policy = anylog_dict['new_policy']

    return policy


def validate_node_policy(anylog_conn:AnyLogConnector, policy_type:str, anylog_configs:dict, exception:bool=False)->bool:
    """
    Validate if (node) policy exists
    :args:
        anylog_conn:AnyLogConnector - REST connection to AnyLog
        policy_type:str - policy type
            - master
            - operator
            - query
            - publisher
        anylog_configs:ddict - AnyLog configurations
        exception:bool - whether to print exceptions
    :params:
        status:bool
        count:int
        where_condition:dict generated where conditions
    :return:
        status
    """
    status = False
    count = 0

    while count < 6:
        if count == 0:
            # check all params
            where_conditions = __build_full_info(anylog_configs=anylog_configs)
            if where_conditions != {}:
                policy = blockchain_calls.get_policy(anylog_conn=anylog_conn, policy_type=policy_type,
                                                     where_conditions=where_conditions, bring_conditions=None,
                                                     bring_values=None, separator=None, view_help=False,
                                                     exception=exception)
            else:
                count = 10
        elif count == 1:
            # check node name + company name for the policy
            where_conditions = __build_name_info(anylog_configs=anylog_configs)
            if where_conditions != {}:
                policy = blockchain_calls.get_policy(anylog_conn=anylog_conn, policy_type=policy_type,
                                                     where_conditions=where_conditions, bring_conditions=None,
                                                     bring_values=None, separator=None, view_help=False,
                                                     exception=exception)
        elif count == 2:
            # networking external IP + TCP port
            where_conditions = __build_network_info(anylog_configs=anylog_configs, external=True, rest=False)
            if where_conditions != {}:
                policy = blockchain_calls.get_policy(anylog_conn=anylog_conn, policy_type=policy_type,
                                                     where_conditions=where_conditions, bring_conditions=None,
                                                     bring_values=None, separator=None, view_help=False,
                                                     exception=exception)
        elif count == 3:
            # networking external IP + REST port
            where_conditions = __build_network_info(anylog_configs=anylog_configs, external=True, rest=True)
            if where_conditions != {}:
                policy = blockchain_calls.get_policy(anylog_conn=anylog_conn, policy_type=policy_type,
                                                     where_conditions=where_conditions, bring_conditions=None,
                                                     bring_values=None, separator=None, view_help=False,
                                                     exception=exception)

        elif count == 4:
            # networking internal/local IP + TCP port
            where_conditions = __build_network_info(anylog_configs=anylog_configs, external=False, rest=False)
            if where_conditions != {}:
                policy = blockchain_calls.get_policy(anylog_conn=anylog_conn, policy_type=policy_type,
                                                     where_conditions=where_conditions, bring_conditions=None,
                                                     bring_values=None, separator=None, view_help=False,
                                                     exception=exception)
        elif count == 5:
            # networking internal/local IP + REST port
            where_conditions = __build_network_info(anylog_configs=anylog_configs, external=False, rest=True)
            if where_conditions != {}:
                policy = blockchain_calls.get_policy(anylog_conn=anylog_conn, policy_type=policy_type,
                                                     where_conditions=where_conditions, bring_conditions=None,
                                                     bring_values=None, separator=None, view_help=False,
                                                     exception=exception)

        if policy != '':
            count = 10
            status = True
        else:
            count += 1

    return status


def declare_node_policy(anylog_conn:AnyLogConnector, policy_type:str, anylog_configs:dict, exception:bool=False)->bool:
    """
    Declare policy in blockchain
    :process:
        1. generate policy
        2. prepare policy
        3. post policy on blockchain
    :args:
        anylog_conn:AnyLogConnector - REST connection to AnyLog
        policy_type:str - policy type
            - master
            - operator
            - query
            - publisher
        anylog_configs:ddict - AnyLog configurations
        exception:bool - whether to print exceptions
    :params:
    """
    status = True
    geo_locatons = {}
    for param in ['node_name', 'company_name', 'external_ip', 'ip', 'anylog_server_port', 'anylog_rest_port']:
        if param not in anylog_configs:
            status = False

    if status is True:
        geo_locatons = find_location.get_location(anylog_conn=anylog_conn, exception=exception)

        if 'hostname' not in anylog_configs:
            anylog_configs['hostname'] = None
        if 'anylog_broker_port' not in anylog_configs:
            anylog_configs['anylog_broker_port'] = None
        if 'cluster_id' not in anylog_configs:
            anylog_configs['cluster_id'] = None
        if 'member' not in anylog_configs:
            anylog_configs['member'] = None
        if 'location' not in anylog_configs:
            anylog_configs['location'] = geo_locatons['location']
        if 'country' not in anylog_configs:
            anylog_configs['country'] = geo_locatons['country']
        if 'state' not in anylog_configs:
            anylog_configs['state'] = geo_locatons['state']
        if 'city' not in anylog_configs:
            anylog_configs['city'] = geo_locatons['city']

        policy = blockchain_support.node_policy(policy_type=policy_type, name=anylog_configs['node_name'],
                                                company=anylog_configs['company_name'],
                                                external_ip=anylog_configs['external_ip'], local_ip=anylog_configs['ip'],
                                                anylog_server_port=anylog_configs['anylog_server_port'],
                                                anylog_rest_port=anylog_configs['anylog_rest_port'],
                                                hostname=anylog_configs['hostname'],
                                                anylog_broker_port=anylog_configs['anylog_broker_port'],
                                                cluster_id=anylog_configs['cluster_id'], member=anylog_configs['member'],
                                                location=anylog_configs['location'], country=anylog_configs['country'],
                                                state=anylog_configs['state'], city=anylog_configs['city'],
                                                exception=exception)

        if blockchain_calls.prepare_policy(anylog_conn=anylog_conn, policy=policy, view_help=False, exception=exception):
            policy = __extract_policy(anylog_conn=anylog_conn, exception=exception)
            if 'platform' not in anylog_configs:
                anylog_configs['platform'] = None
            if 'ledger_conn' not in anylog_configs:
                anylog_configs['ledger_conn'] = None

            if not blockchain_calls.post_policy(anylog_conn=anylog_conn, policy=policy, local_publish=True,
                                                platform=anylog_configs['platform'],
                                                ledger_conn=anylog_configs['ledger_conn'], view_help=False,
                                                exception=exception):
                status = False
                print(f'Failed to POST policy in blockchain')
        else:
            status = False
            print(f'Failed to prepare policy, cannot POST policy in blockchain')
    else:
        print('One or more key configurations is missing')

    return status



