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
        r = requests.get("c")
    except:
        pass
    else:
        try:
            if int(r.status_code) == 200:
                try:
                    location = r.json()['loc']
                except Exception as e:
                    pass
        except:
            pass

    return location


def __format_tables(dbms:str, tables:list)->list:
    """
    Given a list of tables and dbms format for input in blockchain
    :args:
        dbms:str - default dbms
        tables:list - list of tables
    :params:
        tables_list:list - list of tables with their dbms [{dbms: db, table: tbl}]
    :return:
        tables_list
    """
    tables_list = []
    for tbl in tables:
        tables_list.append({'dbms': dbms, 'name': tbl})
    return tables_list


def declare_cluster(config:dict)->dict:
    """
    Declare cluster node based on config
    :args:
        config:dict - config info
    :params:
        cluster:dict - dict object for generic node
    :return:
         cluster
    """
    cluster = {'cluster': {}}
    if 'company_name' in config:
        cluster['cluster']['company'] = config['company_name']
    if 'cluster_name' in config:
        cluster['cluster']['name'] = config['cluster_name']
    elif 'company_name' in config:
        cluster['cluster']['name'] = '%s-cluster' % config['company_name'].lower().replace(' ', '-')
    else:
        cluster['cluster']['name'] = 'new-cluster'
    if 'table' in config:
        cluster['cluster']['table'] = __format_tables(config['default_dbms'], config['table'].split(','))
    else:
        cluster['cluster']['dbms'] = config['default_dbms']
    return cluster


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
    if 'company_name' in config:
        node[config['node_type']]['company'] = config['company_name']

    if 'node_name' in config:
        node[config['node_type']]['name'] = config['node_name']
    elif 'company_name' in config:
        node[config['node_type']]['name'] = '%s-operator' % config['company_name'].lower().replace(' ', '-')
    elif 'node_type' in config:
        node[config['node_type']]['name'] = config['node_type']

    if 'member_id' in config:
        # If member ID fails - skips adding member ID
        try: 
            node[config['node_type']]['member'] = int(config['member_id'])
        except: 
            pass 

    if 'hostname' in config:
         node[config['node_type']]['hostname'] = config['hostname']

    if 'location' in config:
         node[config['node_type']]['loc'] = config['location'] 
    elif location is True:
        node[config['node_type']]['loc'] = __get_location()

    if 'member_id' in config:
        node[config['node_type']]['member'] = config['member_id']

    if 'cluster_id' in config:
        node[config['node_type']]['cluster'] = config['cluster_id']

    if 'default_dbms' in config:
        node[config['node_type']]['dbms'] = config['default_dbms']
    elif 'table' in config:
        node[config['node_type']]['table'] = config['table']

    return node


def declare_generic_policy(policy_type:str, policy_values:dict, location:bool)->dict: 
    """
    Declare location
    :args: 
        policy_type:str - the type of policy (ex. 'sensor' and 'device') 
        policy_values:dict - key-value pairs correlated to device (ex. name, comapny, IP)
        location:bool - for devices and senors -- add a location (lat and long) of the new policy.
                        If set to (True), the location will be the same as that of the node from which the policy 
                        was declared.     
    :params:
        new_policy:dict - policy to declare 
    :return: 
        new_policy
    """
    new_policy = {policy_type: policy_values}
    if isinstance(location, bool) and location is True:
        new_policy[policy_type]['loc'] = __get_location()
    elif isinstanc(location, str):
        new_policy[policy_type]['loc'] = location
    
    return new_policy
        