import anylog_api.anylog_connector as anylog_connector
import anylog_api.blockchain.cmds as blockchain_cmds


def create_cluster_policy(name:str, owner:str, db_name:str=None, table:str=None, parent:str=None):
    """
    Declare cluster policy
    :args:
        name:str - cluster name
        owner:str - company name / cluster owner
    :optional-args:  if specified, then the cluster will only work against given database and/or tabale OR associated with a parent cluster
        db_name:str - specific database name
        table:str - specific table name
        parent:str - cluster parent ID
    :params:
        node_policy
    :return:
        node_policy
    """
    cluster_policy = {
        "cluster": {
            "name": name,
            "company": owner
        }
    }
    if db_name and parent:
        cluster_policy['cluster']['parent'] = parent
    if db_name and table:
        cluster_policy['cluster']['table'] = [
            {
                "dbms": db_name,
                "table": table
            }
        ]
    elif db_name:
        cluster_policy['cluster']['dbms'] = db_name
    return cluster_policy

def create_node_policy(node_type:str, node_name:str, owner:str, ip:str, anylog_server_port:int, anylog_rest_port:str,
                       local_ip:str=None, anylog_broker_port:int=None, cluster_id:str=None, is_main:bool=False,
                       location:dict=None, other_params:dict=None, scripts:list=None):
    """
    Declare dictionary object which will be used as the policy for the node
    :sample-policy:
        {'operator' : {
            'name' : 'syslog-operator2',
            'company' : 'AnyLog Co.',
            'ip' : '172.105.219.25',
            'local_ip' : '172.105.219.25',
            'port' : 32148,
            'rest_port' : 32149,
            'broker_port' : 32150,
            'main' : False,
            'cluster' : '2957ab8c837c52d9160c4b60041cbf08',
            'loc' : '35.6895,139.6917',
            'country' : 'JP',
            'city' : 'Tokyo',
        }}
    :args:
        node_type:str - node type (ex. master, operator, query)
        node_name:str - node name
        owner:str - owner / company that the node is associated with
        ip:str - (external) IP of the node
        local_ip:str - (local) Ip of the node
        anylog_server_port:int - TCP port value
        anylog_rest_port:int - REST port value
        anylog_broker_port:int - Message broker port
        cluster_id:str - for Operator, the cluster ID
        is_main:bool - for operator whether the node is a primary or secondary
        location:dict - geolocation of the node
            loc:str - coordinates
            country:str
            city:str
            ...
        other_params:dict - dictionary of non-"default" params
        scripts:list - any commands to be executed as part of the policy
    :params:
        node_type:dict - generated AnyLog policy
    :return:
        node_policy
    """
    node_policy = {
        node_type: {
            "name": node_name,
            "company": owner,
            "ip": ip,
            "port": anylog_server_port,
            "rest": anylog_rest_port
        }
    }

    if local_ip:
        node_policy[node_type]['local_ip'] = local_ip
    if anylog_broker_port:
        node_policy[node_type]['broker'] = anylog_broker_port
    if node_type == 'operator':
        node_policy[node_type]['main'] = is_main
        if cluster_id:
            node_policy[node_type]['cluster'] = cluster_id
        elif not cluster_id:
            raise ValueError('Error: Unable to create operator policy, must have a cluster to associate with')
    if location:
        for loc in location:
            node_policy[node_type][loc] = location[loc]
    if other_params:
        for param in other_params:
            node_policy[node_type][param] = other_params[param]
    if scripts:
        node_policy[node_type]['script'] = scripts

    return node_policy


