import requests

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
