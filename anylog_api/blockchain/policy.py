import anylog_api.anylog_connector as anylog_connector
from anylog_api.__support__ import json_dumps
from anylog_api.generic.geolocation import get_geolocation


def __base_policy(name:str, company:str, external_ip:str, local_ip:str, anylog_server_port:int, anylog_rest_port:int,
                  anylog_broker_port:int=None, tcp_bind:bool=False, rest_bind:bool=False, broker_bind:bool=False)->dict:
    """
    Generate base for policy
    """
    policy = {
        "name": name,
        "company": company,
        "ip": external_ip,
        "local_ip": local_ip,
        "port": anylog_server_port,
        "rest_port": anylog_rest_port
    }

    if anylog_broker_port:
        policy['broker_port'] = anylog_broker_port
    if tcp_bind is True:
        policy["ip"] = local_ip
    if rest_bind is True:
        policy['rest_ip'] = local_ip
    if broker_bind is True:
        policy['broker_ip'] = local_ip

    return policy


def cluster_policy(name:str, company:str, policy_id:str=None, dbms:str=None, table:str=None, parent:str=None,
                   other_params:dict={})->str:
    """
    Create cluster policy
    :args:
        name:str - policy name
        company:str - company name (cluster owner)
        policy_id:str - user defined policy ID
        parent:str - policy ID for parent cluster
        dbms:str - logical database name
        table:str - physical table associated with cluster
        other_params:dict - key:value pairs for other params in policy
        scripts:list - list of commands to execute
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

    if other_params:
        for param in other_params:
            policy["cluster"][param] = other_params[param]

    return json_dumps(policy, indent=2)


def node_policy(conn:anylog_connector.AnyLogConnector, node_type:str, name:str, company:str, external_ip:str,
                local_ip:str, anylog_server_port:int, anylog_rest_port:int, anylog_broker_port:int=None,
                tcp_bind:bool=False, rest_bind:bool=False, broker_bind:bool=False, cluster_id:str=None,
                set_geolocation:bool=True, policy_id:str=None, other_params:dict={}, scripts:list=[],
                destination:str=None, exception:bool=False)->str:
    """
    Create node policy
        - master
        - operator
        - query
        - publisher
    :args:
        node_type:str - node type
        name:str - policy name
        company:str - company name (cluster owner)
        policy_id:str - user defined policy ID
        external_ip:str - external IP
        local_ip:str - local IP
        anylog_server_port:int - port used for TCP
        anylog_rest_port:int - port used for REST
        anylog_broker_port:int - port used for message broker
        tcp_bind:bool - bind TCP port
        rest_bind:bool - bind REST port
        broker_bind:bool - bind message broker port
        set_geolocation:bool - whether to set geolocation
        cluster_id:str - for Operator, associated cluster ID
        other_params:dict - key:value pairs for other params in policy
        scripts:list - list of commands to execute
        destination:str - remote connection to send request against
        exception:bool - whether to print exceptions
    :params:
        policy:dict - generated policy
    :return:
        serialized-JSON policy
    :sample policy:
        {"publisher": {
              "hostname": "al-live-publisher",
              "name": "anylog-publisher-node",
              "ip": "172.104.180.110",
              "local_ip": "172.104.180.110",
              "company": "AnyLog",
              "port": 32248,
              "rest_port": 32249,
              "loc": "1.2897,103.8501",
              "country": "SG",
              "state": "Singapore",
              "city": "Singapore",
              "id": "d2ef8f32b3d894f4d721275435e7d05d",
              "date": "2022-06-06T00:38:45.838582Z",
              "ledger": "global"
        }}
    """
    policy = {
        node_type: __base_policy(name=name, company=company, external_ip=external_ip, local_ip=local_ip,
                                 anylog_server_port=anylog_server_port, anylog_rest_port=anylog_rest_port,
                                 anylog_broker_port=anylog_broker_port, tcp_bind=tcp_bind, rest_bind=rest_bind,
                                 broker_bind=broker_bind)
    }

    if node_type == 'operator' and cluster_id:
        policy[node_type]['cluster'] = cluster_id

    if set_geolocation is True:
        geolocation = get_geolocation(conn=conn, destination=destination, view_help=False, return_cmd=False,
                                      exception=exception)
        for key in ['loc', 'country', 'state', 'city']:
            policy[node_type][key] = geolocation[key]
    if other_params and isinstance(other_params, dict):
        for param in other_params:
            policy[node_type][param] = other_params[param]
    if scripts and isinstance(scripts, list):
        policy[node_type]['scripts'] = scripts
    if policy_id:
        policy[node_type]['id'] = policy_id

    return json_dumps(policy, indent=2)


def config_policy(node_type:str, name:str, company:str, external_ip:str='"!external_ip"', local_ip:str='"!local_ip"',
                  anylog_server_port:int='"!anylog_server_port"', anylog_rest_port:int='"!anylog_rest_port"',
                  anylog_broker_port:int=None, tcp_bind:bool=False, rest_bind:bool=False, broker_bind:bool=False,
                  policy_id:str=None, other_params:dict={}, scripts:list=[])->str:
    """
    Generate configuration policy
    :args:
        node_type:str - node type
        name:str - policy name
        company:str - company name (cluster owner)
        policy_id:str - user defined policy ID
        external_ip:str - external IP
        local_ip:str - local IP
        anylog_server_port:int - port used for TCP
        anylog_rest_port:int - port used for REST
        anylog_broker_port:int - port used for message broker
        tcp_bind:bool - bind TCP port
        rest_bind:bool - bind REST port
        broker_bind:bool - bind message broker port
        other_params:dict - key:value pairs for other params in policy
        scripts:list - list of commands to execute
        destination:str - remote connection to send request against
        exception:bool - whether to print exceptions
    :params:
        policy:dict - generated policy
    :return:
        serialized-JSON policy
    """
    policy = {'config': __base_policy(name=name, company=company, external_ip=external_ip, local_ip=local_ip,
                                      anylog_server_port=anylog_server_port, anylog_rest_port=anylog_rest_port,
                                      anylog_broker_port=anylog_broker_port, tcp_bind=tcp_bind, rest_bind=rest_bind,
                                      broker_bind=broker_bind)
              }

    policy['config']['node_type'] = node_type

    if other_params and isinstance(other_params, dict):
        for param in other_params:
            policy[node_type][param] = other_params[param]
    if scripts and isinstance(scripts, list):
        policy[node_type]['scripts'] = scripts
    if policy_id:
        policy[node_type]['id'] = policy_id

    return json_dumps(policy, indent=2)


def table_policy(db_name:str, table:str, create_stmt:str, policy_id:str=None, other_params:dict={})->str:
    """
    Create table policy - automatically gets created with new table
    :args:
        db_name:str - logical database name
        table:str - name of table being generated
        create_stmt:str - SQL create statement
        policy_id:str - user define ID
        other_params:dict - other params to add to policy
    :params:
        policy:dict - generated policy
    """
    policy = {
        "table": {
            "name": table,
            "dbms": db_name,
            "create": create_stmt
        }
    }

    if policy_id:
        policy['table']['id'] = policy_id
    if other_params and isinstance(other_params, dict):
        for param in other_params:
            policy['table'][param] = other_params[param]

    return json_dumps(contnet=policy, indent=2)


def anmp_policy(original_policy_id:str, name:str, company:str, other_params:dict={}, scripts:list=[], policy_id:str=None)->str:
    """
    generate anylog network mapping policy (ANMP) - which is used to update / overwrite an existing policy
    :args:
        original_policy_id:str - original policy ID
        name:str - ANMP policy name
        company:str - ANMP policy company / owner
        other_params:dict - params to add to policy
        scripts:list - list of policies
        policy_id:Str - user define policy
    :params:
        policy:dict - generated policy
    :return:
        serialized policy
    """
    policy = {
        "anmp": {
            "name": name,
            "company": company,
            original_policy_id: {}
        }
    }

    if other_params and isinstance(other_params, dict):
        for param in other_params:
            policy['anmp'][original_policy_id][param] = other_params[param]
    if scripts and isinstance(scripts, list):
        policy['anmp'][original_policy_id]['scripts'] = scripts
