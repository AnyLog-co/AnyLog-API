"""
config
"""
import anylog_api.anylog_connector as anylog_connector
from anylog_api.__support__ import json_dumps
from anylog_api.generic.find_location import get_location
from anylog_api.generic.scheduler import run_scheduler1
from anylog_api.blockchain.cmd import blockchain_sync

def __base_policy(name:str, company:str, policy_id:str=None, external_ip:str='!external_ip',
                  local_ip='!ip', rest_ip:str=None, broker_ip:str=None, server_port='!anylog_server_port',
                  rest_port='!anylog_rest_port', broker_port=None, server_bind:bool=False)->str:
    policy = {
        "name": name,
        "company": company,
        "ip": external_ip,
        "local_ip": local_ip,
        "port": server_port,
        "rest_port": rest_port
    }

    if policy_id:
        policy['id'] = policy_id

    if server_bind is True:
        policy['ip'] = local_ip
    if rest_ip:
        policy['rest_ip'] = rest_ip
    if broker_port:
        policy['broker_port'] = broker_port
        if broker_ip:
            policy['broker_ip'] = broker_ip

    return policy

def config_policy(node_type:str, name:str, company:str, policy_id:str=None, external_ip:str='!external_ip',
                  local_ip='!ip', rest_ip:str=None, broker_ip:str=None, server_port='!anylog_server_port',
                  rest_port='!anylog_rest_port', broker_port=None, server_bind:bool=False, scripts:list=[],
                  source:str='master', time:str='30 seconds', dest:str='file', connection:str='!ledger_conn',)->str:
    policy = {
        'config': __base_policy(name=name, company=company, policy_id=policy_id, external_ip=external_ip,
                                local_ip=local_ip, rest_ip=rest_ip, broker_ip=broker_ip, server_port=server_port,
                                rest_port=rest_port, broker_port=broker_port, server_bind=server_bind)
    }

    policy['config']['script'] = [
        run_scheduler1(conn=None, scheduler_id=1, destination=None, return_cmd=True),
        blockchain_sync(conn=None, source=source, time=time, dest=dest, connection=connection, return_cmd=True)
    ]

    if node_type == 'operator':





def generic_policy(conn:anylog_connector.AnyLogConnector, node_type:str, name:str, company:str,
                   policy_id:str=None, external_ip:str='!external_ip', local_ip='!ip', rest_ip:str=None,
                   broker_ip:str=None, server_port='!anylog_server_port', rest_port='!anylog_rest_port',
                   broker_port=None, server_bind:bool=False, cluster_id:str=None, geoloc:str=None, country:str=None,
                   state:str=None, city:str=None, scripts:list=[], exeception:bool=False)->str:
    """
    Create node policy
        - master
        - operator
        - query
        - publisher
    :args:
        name:str - cluster name
        company:str - company name (cluster owner)
        policy_id:str - user defined policy ID
        external_ip:str - external IP
        local_ip:str - local IP
        rest_ip:str - rest IP (REST_BIND = True)
        broker_ip:str - broker IP (BROKER_BIND = True)
        server_port - Server port
        rest_port - REST port
        broker_port - Message broker port
        server_bind:bool - TCP port bind (if set replace external ip with ip)
        cluster_id:str - cluster id (used in operator)
        # geolocation
        geoloc:str - geo coordinates
        country:str
        state:str
        city:str
    :params:
        policy:dict - generated policy
        location:list - if geolocation not found, get location
    :return:
        serialized-JSON policy
    """
    policy = {
        node_type: __base_policy(name=name, company=company, policy_id=policy_id, external_ip=external_ip,
                                 local_ip=local_ip, rest_ip=rest_ip, broker_ip=broker_ip, server_port=server_port,
                                 rest_port=rest_port, broker_port=broker_port, server_bind=server_bind)
    }

    if policy_id:
        policy[node_type]['id'] = policy_id

    if server_bind is True:
        policy[node_type]['ip'] = local_ip
    if rest_ip:
        policy[node_type]['rest_ip'] = rest_ip
    if broker_port:
        policy[node_type]['broker_port'] = broker_port
        if broker_ip:
            policy[node_type]['broker_ip'] = broker_ip
    if node_type == 'operator' and cluster_id:
        policy[node_type]['cluster'] = cluster_id

    if geoloc:
        policy[node_type]['loc'] = geoloc
        if country:
            policy[node_type]['country'] = country
        if state:
            policy[node_type]['state'] = state
        if city:
            policy[node_type]['city'] = city
    else:
        location = get_location(anylog_conn=conn, exception=exeception)
        policy[node_type]['loc'] = location['loc']
        policy[node_type]['country'] = location['country']
        policy[node_type]['state'] = location['state']
        policy[node_type]['city'] = location['city']

    if scripts:
        policy[node_type]['script'] = scripts

    return policy


def cluster_policy(name:str, company:str, policy_id:str=None, dbms:str=None, table:str=None, parent:str=None)->str:
    """
    Create cluster policy
    :args:
        name:str - cluster name
        company:str - company name (cluster owner)
        policy_id:str - user defined policy ID
        parent:str - parent cluster policy
        dbms:str - logical database name
        table:str - physicl table name
        parent:str - parent cluster ID
    :params:
        policy:dict - generated policy
    :return:
        serialized-JSON policy
    :sample-policy:
        # only name + company
        {"cluster" : {
              "name" : "litsanleandro-cluster1",
              "company" : "Lit San Leandro",
        }}
        # datababase
        {"cluster" : {
              "name" : "litsanleandro-cluster1",
              "company" : "Lit San Leandro",
              "dbms": "my_databaase"
        }}
        # everything
        {"cluster" : {
              "name" : "litsanleandro-cluster1",
              "company" : "Lit San Leandro",
              "table": [{
                "dbms": "my_database",
                "name": "sensors_49",
              }]
              "parent": "0015392622f3eaac70eafa4311fc2338"
        }}
    """
    policy = {
        "cluster": {
            "name": name,
            "company": company
        }
    }

    if policy_id is not None:
        policy['cluster']['id'] = policy_id

    if dbms is not None and table is not None and parent is not None:
        policy["cluster"]["table"] = [
            {
                "dbms": dbms,
                "table": table
            }
        ]
        policy["cluster"]["parent"] = parent
    elif dbms is not None:
        policy["cluster"]["dbms"] = dbms

    return json_dumps(policy, indent=2)



