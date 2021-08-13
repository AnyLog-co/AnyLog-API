import requests

import __init__
import rest.anylog_api as anylog_api
import rest.blockchain_cmd as blockchain_cmd

def __get_location()->str:
    """
    Get location using https://ipinfo.io/json
    :param:
        location:str - location information from request (default: 0.0, 0.0)
    :return:
        location
    """
    location = "0.0, 0.0"
    try:
        r = requests.get("https://ipinfo.io/json")
    except Exception as e:
        pass
    else:
        if r.status_code == 200:
            try:
                location = r.json()['loc']
            except Exception as e:
                pass
    return location



def declare_node(config:dict, location:bool=True)->dict: 
    """
    Declare generic node based on config
    :args: 
        config:dict - config info
        location:bool - whether or to add location to policy if not in config
    :params: 
        node:dict - dict object for generic node
    :return: 
         node 
    """
    if 'node_type' not in config: 
        return {} 

    node = {config['node_type']: {
        'ip':        config['external_ip'],
        'local_ip':  config['ip'],
        'port':      int(config['anylog_server_port']),
        'rest_port': int(config['anylog_rest_port']), 
    }}
    if 'node_name' in config: 
        node[config['node_type']]['name'] = config['node_name']
    elif 'node_type' in config: 
        node[config['node_type']]['name'] = config['node_type'] 
    if 'hostname' in config:
         node[config['node_type']]['hostname'] = config['hostname']
    if 'location' in config: 
         node[config['node_type']]['loc'] = config['location'] 
    elif location is True:
        node[config['node_type']]['loc'] = __get_location()

    return node 

def  declare_operator(conn:anylog_api.AnyLogConnect, config:dict, exception:bool=False)->bool:
    """
    Given a generic node, enhance it with oprator config
    :args: 
        node:dict - generic node to enhance
        config:dict - config info
        cluster_id:str - clustter ID if valid
    :return: 
        node
    """
    create_operator = True
    if blockchain_cmd.pull_json(conn=conn, master_node=config['master_node'], exception=exception):
        blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type='operator', where=['name=%s' % config['cluster_name']])
    """
    if 'enable_cluster' in config and config['enable_cluster'] == 'true':
        if 'cluster_name' in config and
            blockchain = blockchain_cmd.blockchain_get(conn=conn, policy_type='cluster', where=['name=%s' % config['cluster_name']])
            print(blockchain)
    """