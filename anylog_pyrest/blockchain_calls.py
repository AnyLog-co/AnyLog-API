import json
from anylog_connection import AnyLogConnection
from generic_get_calls import get_location
from support import print_error

def blockchain_sync(anylog_conn:AnyLogConnection, blockchain_source:str, blockchain_destination:str, sync_time:str,
                    ledger_conn:str, exception:bool=False)->bool:
    """
    Enable automatic blockchain sync process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/blockchain%20configuration.md#synchronize-the-blockchain-data-with-a-local-copy-every-30-seconds
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        blockchain_source:str - source where data is coming from (default: master node)
        blockchain_destination:str - destination where data will be stored locally (default: file)
        sync_time:str - how often to sync
        ledger_conn:str - connection to blockchain ledger (for master use IP:Port)
        exception:bool - Whether or not to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status = True
    headers = {
        "command": f"run blockchain sync where source={blockchain_source} and time={sync_time} and dest={blockchain_destination} and connection={ledger_conn}",
        "User-Agent": "AnyLog/1.23"
    }
    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True and r is False:
            print_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def get_policy(anylog_conn:AnyLogConnection, policy_type:str, name:str, company:str, local_ip:str="",
                        anylog_server_port:int="", exception:bool=False)->dict:
    """
    check whether policy exists, if exists then returns policy else returns empty dict
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        policy_type:str - policy type
        name:str - policy name
        company:str - Company which owns this policy
        local_ip:str - local IP
        anylog_server_port:int - AnyLog TCP port
        exception:bool - Whether or not to print exceptions
    :params:
        policy:dict - policy to return
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        if succcess returns policy, else returns {} 
    """
    headers = {
        'command': f"blockchain get {policy_type} where name={name} and company={company}",
        "User-Agent": "AnyLog/1.23"
    }
    if local_ip != "":
        headers["command"] += f" and local_ip={local_ip}"
    if anylog_server_port != "":
        headers["command"] += f" and tcp={anylog_server_port}"
    if policy_type == "cluster":
        headers['command'] += " bring.first"

    r, error = anylog_conn.get(headers=headers)
    if exception is True and r is False:
        print_error(error_type='GET', cmd=headers['command'], error=error)
    else:
        try:
            policy = r.json()
        except:
            policy = {}

    return policy


def create_policy(policy_type:str, name:str, company:str, db_name:str=None, hostname:str="", external_ip:str="",
                  local_ip:str="", anylog_server_port:int="", anylog_rest_port:int="", location:str="", country:str="", 
                  state:str="", city="", cluster_id:str="", member:int="", exception:bool=False)->dict:
    """
    create AnyLog policy
    :sample policy: 
    cluster - 
        {'cluster': {
            'name': 'new-cluster',
            'company': 'AnyLog', 
            'dbms': 'test'
        }}
    (master) node - 
        {'master': {
            'name': 'anylog-node',
            'company': 'AnyLog',
            'hostname': 'anylog-test',
            'ip': '24.23.250.144',
            'local_ip': '10.0.0.5',
            'port': 2048,
            'rest_port': 2049,
            'loc': '37.5395,-122.2998',
            'country': 'US',
            'state': 'California',
            'city': 'San Mateo'
        }}
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        policy_type:str - policy type
        name:str - policy name
        company:str - Company which owns this policy
        db_name:str - logical database name (for cluster policy)
        hostname:str - hostname
        external_ip:str - external IP
        local_ip:str - local IP
        anylog_server_port:int - AnyLog TCP port
        anylog_rest_port:int - AnyLog REST port
        location:str - coordinates
        country:str - country
        state:str - region within country
        city:str - city within state
        cluster_id:str - cluster ID (operator only)
        member:int - [optional] member ID for operator (for operator only)
        exception:bool - whether to print exception(s) or not
    :params:
        policy:dict - generated policy
    :return: 
        policy
    """
    policy = {policy_type: {
        'name': name,
        'company': company
    }}

    if policy_type == 'cluster' and db_name is not None:
        policy[policy_type]['dbms'] = db_name
    elif policy_type == 'cluster' and db_name is None:
        policy = {}
        if exception is True:
            print('Cluster policy must have a logical database associated to it')
    else:
        policy[policy_type]['hostname'] = hostname
        policy[policy_type]['ip'] = external_ip
        policy[policy_type]['local_ip'] = local_ip
        policy[policy_type]['port'] = int(anylog_server_port)
        policy[policy_type]['rest_port'] = int(anylog_rest_port)

        if all(param == "" for param in [location, country, state, city]):
            location_info = get_location(exception=exception)
            location = location_info['loc']
            country = location_info['country']
            state = location_info['region']
            city = location_info['city']
        policy[policy_type]['loc'] = location
        policy[policy_type]['country'] = country
        policy[policy_type]['state'] = state
        policy[policy_type]['city'] = city

        if policy_type == 'operator' and cluster_id != "":
            policy[policy_type]['cluster'] = cluster_id
        if policy_type == "operator" and member != "":
            policy[policy_type]['member'] = int(member)

    return policy
