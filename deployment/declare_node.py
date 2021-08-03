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
     node = {
         'name':      config['node_name'], 
         'ip':        config['external_ip'],
         'local_ip':  config['ip'],
         'port':      config['anylog_server_port'],
         'rest_port': config['anylog_rest_port'], 
     }
     if 'hostname' in  config: 
         node['hostname'] = config['hostname']
     if 'location' in config: 
         node['loc'] = config['location'] 

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
        node['member_id'] = config['member_id']
    if cluster_id != None: 
        node['cluster_id'] = cluster_id
    else: 
        if 'default_dbms' in config: 
            node['default_dbms'] = config['default_dbms']
        if 'table' in config: 
            node['table'] = config['table'] 

    return node
