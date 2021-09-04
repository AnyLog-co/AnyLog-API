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
        tables_list.append({'dbms': dbms, 'table': tbl})
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
    cluster = {'cluster': {
        'company': config['company_name'],
        'name': config['cluster_name'],
    }}
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
    if 'default_dbms' in config:
        node[config['node_type']]['dbms'] = config['default_dbms']
    if 'cluster_id' in config:
        node[config['node_type']]['cluster'] = config['cluster_id']
    elif 'table' in config:
        node[config['node_type']]['table'] = config['table']
    return node 
