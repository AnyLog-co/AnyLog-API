def declare_node(config:dict)->dict: 
    """
    Declare generic node based on config
    :args: 
        conn:str - REST connection information
        config:dict - config info
    :params: 
        node:dict - dict object for generic node
     :return: 
         node 
     """
     if 'node_type' not in config: 
         return {} 

     node = {config['node_type']: 
         'ip':        config['external_ip'],
         'local_ip':  config['ip'],
         'port':      int(config['anylog_server_port']),
         'rest_port': int(config['anylog_rest_port']), 
     }
     if 'node_name' in config: 
        node[config['node_type']]['name'] = config['node_name']
     elif 'node_type' in config: 
        node[config['node_type']]['name'] = config['node_type'] 
     if 'hostname' in  config: 
         node[config['node_type']]['hostname'] = config['hostname']
     if 'location' in config: 
         node[config['node_type']]['loc'] = config['location'] 

    return node 

def  declare_operator(node:dict, config:dict, cluster_id:str=None)->dict: 
    """
    Given a generic node, enhance it with oprator config
    :args: 
        node:dict - generic node to enhance
        config:dict - config info
        cluster_id:str - clustter ID if valid
    :return: 
        node
    """
    if 'member_id' in config: 
        node[config['node_type']]['member_id'] = config['member_id']
    if cluster_id != None: 
        node[config['node_type']]['cluster_id'] = cluster_id
    else: 
        if 'default_dbms' in config: 
            node[config['node_type']]['default_dbms'] = config['default_dbms']
        if 'table' in config: 
            node[config['node_type']]['table'] = config['table'] 

    return node
