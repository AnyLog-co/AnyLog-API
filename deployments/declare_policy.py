import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from find_location import get_location

from anylog_connection import AnyLogConnection
import blockchain_calls as blockchain_calls
import support


def declare_policy(anylog_conn:AnyLogConnection, node_type:str, node_name:str, company_name:str, hostname:str,
                   external_ip:str, local_ip:str, server_port:int, rest_port:int, member:int=None,
                   cluster_name:str=None, location:str=None, country:str='Unknown',state:str='Unknown',
                   city:str='Unknown', exception:bool=False):
    """
    :generic-policy:
        1. check if policy already exists
        2. if not create policy
        3. declare on blockchain
    :for operator:
        1. check if operator exists
        2. if not check if cluster exists
        3. declare cluster
        4. declare operator
    """
    cluster_id = None
    if location is None:
        location, country, state, city = get_location(anylog_conn=anylog_conn)


    policy  = blockchain_calls.get_policy(anylog_conn=anylog_conn, policy_type=node_type, name=node_name,
                                               company=company_name, local_ip=local_ip, exception=exception)

    if policy != {}:
        return

    if node_type == 'operator'
        while policy == {}:
            policy = blockchain_calls.get_policy(anylog_conn=anylog_conn, policy_type='cluster', name=cluster_name,
                                                 company_name=company_name)
            if policy == {}:
                blockchain_calls.create_policy(policy_type='cluster', name=cluster_name, company=company_name,
                                               )


    # policy = blockchain_calls.create_anylog_policy(policy_type=node_typ, name=node_name, company=company_name,
    #                                                hostname=hostname, external_ip=external_ip, local_ip=local_ip,
    #                                                anylog_server_port=server_port, anylog_rest_port=rest_port,
    #                                                location=location, country=country, state=state, city=city,
    #                                                exception=exception)
    
