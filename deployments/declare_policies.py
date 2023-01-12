import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'python_rest'))

from anylog_connection import AnyLogConnection
import blockchain_calls
import blockchain_policies
import find_location
import support


def __get_policy_id(anylog_conn:AnyLogConnection, policy_type:str, name:str, company:str, local_ip:str="",
               anylog_server_port:int=None, exception:bool=False)->str:
    """
    Extract policy ID
    :args:
        anylog_conn:AnyLogConnection - Connection to AnyLog node
        policy_type:str - get policy type
        name:str - policy name
        company:str - company policy is associated with
        local_ip:str - IP address of node policy is created against
        anylog_server_port:int - AnyLog TCP port for given AnyLog node
        exception:bool - whether ro print exceptions
    :params:
        policy_id:str - Policy ID
        policy:dict - policy from ledger (if exists)
    :return:
        None if policy DNE, else ID
    """
    policy_id = None
    policy = blockchain_calls.get_policy(anylog_conn=anylog_conn, policy_type=policy_type, name=name, company=company,
                                         local_ip=local_ip, anylog_server_port=anylog_server_port, exception=exception)
    if policy != {}:
        policy_id = policy[policy_type]['id']

    return policy_id


def __declare_policy(anylog_conn:AnyLogConnection, policy_type:str, name:str, company:str, hostname:str=None,
                     external_ip:str=None, local_ip:str=None, anylog_server_port:int=None, anylog_rest_port:int=None,
                     cluster_id:str=None, member:str=None, db_name:str=None, location:str=None, country:str=None,
                     state:str=None, city:str=None, exception:bool=False)->str:
    """
    Declare policy in blockchain
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog via REST
        policy_type:str - policy type (master, publisher or query)
        name:str - policy name
        company:str - company associated with policy
        hostname:str - host of node policy resides on
        external_ip:str / local_ip:int - IP information of the machine
        anylog_server_port:int / anylog_rest_port:int - TCP + REST ports
        cluster_id:str - ID of cluster operator is associated with
        member:int - operator member ID
        location:str / country:str / state:str / city:str - location of the machine
        exception:bool - whether to print exception
    :params:
        policy_id:str - extracted policy ID
        policy:dict - policy to be published on blockchain
        str_policy:str - policy a JSON string
    :return:
        policy_id
    """
    policy_id = __get_policy_id(anylog_conn=anylog_conn, policy_type=policy_type, name=name, company=company,
                                local_ip=local_ip, anylog_server_port=anylog_server_port, exception=exception)
    if policy_id is None:
        if policy_type in ['master', 'publisher', 'query']:
            policy = blockchain_policies.create_generic_policy(policy_type=policy_type, name=name, company=company,
                                                               hostname=hostname, external_ip=external_ip,
                                                               local_ip=local_ip, anylog_server_port=anylog_server_port,
                                                               anylog_rest_port=anylog_rest_port, location=location,
                                                               country=country, state=state, city=city)
        elif policy_type == 'operator':
            policy = blockchain_policies.create_operator_policy(policy_type='operator', name=name, company=company,
                                                               hostname=hostname, external_ip=external_ip,
                                                               local_ip=local_ip, anylog_server_port=anylog_server_port,
                                                               anylog_rest_port=anylog_rest_port, cluster_id=cluster_id,
                                                               member=member, location=location, country=country,
                                                               state=state, city=city)
        elif policy_type == 'cluster':
            policy = blockchain_policies.create_cluster_policy(name=name, company=company, db_name=db_name)

        str_policy = support.json_dumps(content=policy, exception=exception)
        policy = blockchain_calls.prepare_policy(anylog_conn=anylog_conn, policy=str_policy, exception=exception)
        if policy == {}:
            print(f'Failed to prepare policy of type {policy_type}')
        else:
            policy = support.convert_literal(content=policy, exception=exception)
            policy_id = policy[policy_type]['id']

        # if fails we remove the policy_id
        if blockchain_calls.post_policy(anylog_conn=anylog_conn, policy=policy, exception=exception) is False:
            print(f'Failed to insert {policy_type} policy into blockchain')
            policy_id = None

    return policy_id


def declare_policies(anylog_conn:AnyLogConnection, node_type:str, name:str, company:str, hostname:str, external_ip:str,
                     local_ip:str, anylog_server_port:int, anylog_rest_port:int, db_name:str=None, cluster_name:str=None,
                     member:int=None, location:str=None, country:str=None, state:str=None, city:str=None,
                     exception:bool=False):
    """
    Declare AnyLog policies on blockchain
    :process:
        0. if location is not preset then get location
        1. check if policy exists
        2. if not create it
        3. prepare it
        4. publish it
        for operator we first do the same process with cluster node
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog via REST
        policy_type:str - policy type (master, publisher or query)
        name:str - policy name
        company:str - company associated with policy
        hostname:str - host of node policy resides on
        external_ip:str / local_ip:int - IP information of the machine
        anylog_server_port:int / anylog_rest_port:int - TCP + REST ports
        cluster_id:str - ID of cluster operator is associated with
        member:int - operator member ID
        location:str / country:str / state:str / city:str - location of the machine
        exception:bool - whether to print exception
    """
    _location, _country, _state, _city = find_location.get_location(anylog_conn=anylog_conn, exception=exception)
    if location is None:
        location = _location
    if country is None:
        country = _country
    if state is None:
        state = _state
    if city is None:
        city = _city

    if node_type == 'ledger':
        __declare_policy(anylog_conn=anylog_conn, policy_type='master', name=name, company=company, hostname=hostname,
                         external_ip=external_ip, local_ip=local_ip, anylog_server_port=anylog_server_port,
                         anylog_rest_port=anylog_rest_port, location=location, country=country, state=state, city=city,
                         member=None, exception=exception)
    elif node_type == 'publisher':
        __declare_policy(anylog_conn=anylog_conn, policy_type='publisher', name=name, company=company,
                         hostname=hostname, external_ip=external_ip, local_ip=local_ip,
                         anylog_server_port=anylog_server_port, anylog_rest_port=anylog_rest_port, location=location,
                         country=country, state=state, city=city, member=None, exception=exception)
    elif node_type == 'operator':
        cluster_id = __declare_policy(anylog_conn=anylog_conn, policy_type='cluster', name=cluster_name,
                                      db_name=db_name, company=company, exception=exception)
        __declare_policy(anylog_conn=anylog_conn, policy_type='operator', name=name, company=company, hostname=hostname,
                         external_ip=external_ip, local_ip=local_ip, anylog_server_port=anylog_server_port,
                         anylog_rest_port=anylog_rest_port, cluster_id=cluster_id, member=member, location=location,
                         country=country, state=state, city=city, exception=exception)
    elif node_type == 'query':
        __declare_policy(anylog_conn=anylog_conn, policy_type='publisher', name=name, company=company,
                         hostname=hostname, external_ip=external_ip, local_ip=local_ip,
                         anylog_server_port=anylog_server_port, anylog_rest_port=anylog_rest_port, location=location,
                         country=country, state=state, city=city, member=None, exception=exception)
    elif node_type == 'standalone':
        __declare_policy(anylog_conn=anylog_conn, policy_type='master', name=name, company=company, hostname=hostname,
                         external_ip=external_ip, local_ip=local_ip, anylog_server_port=anylog_server_port,
                         anylog_rest_port=anylog_rest_port, location=location, country=country, state=state, city=city,
                         member=None, exception=exception)
        cluster_id = __declare_policy(anylog_conn=anylog_conn, policy_type='cluster', name=cluster_name,
                                      db_name=db_name, company=company, exception=exception)
        __declare_policy(anylog_conn=anylog_conn, policy_type='operator', name=name, company=company, hostname=hostname,
                         external_ip=external_ip, local_ip=local_ip, anylog_server_port=anylog_server_port,
                         anylog_rest_port=anylog_rest_port, cluster_id=cluster_id, member=member, location=location,
                         country=country, state=state, city=city, exception=exception)
    elif node_type == 'standalone-publisher':
        __declare_policy(anylog_conn=anylog_conn, policy_type='master', name=name, company=company, hostname=hostname,
                         external_ip=external_ip, local_ip=local_ip, anylog_server_port=anylog_server_port,
                         anylog_rest_port=anylog_rest_port, location=location, country=country, state=state, city=city,
                         member=None, exception=exception)
        __declare_policy(anylog_conn=anylog_conn, policy_type='publisher', name=name, company=company,
                         hostname=hostname, external_ip=external_ip, local_ip=local_ip,
                         anylog_server_port=anylog_server_port, anylog_rest_port=anylog_rest_port, location=location,
                         country=country, state=state, city=city, member=None, exception=exception)
    else:
        print(f'Unable to declare policy of type {node_type}')







