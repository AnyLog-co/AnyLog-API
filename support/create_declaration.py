"""
The following configures AnyLog node policy based on the provided configuration
"""
import datetime
import requests
from importlib.util import find_spec

try: 
    import geocoder
except: 
    pass 


def __validate_internet()->bool: 
    """
    Validate internet connection
    :params: 
        status:bool 
        r:requests.models.Response - request output
    :return: 
        if succcess return True, else False
    """
    status = True
    try: 
        r = requests.get('https://google.com', timeout=10)
    except: 
        status = False
    else:
        if int(r.status_code) != 200:
            status = False
    return status 


def __get_location(ip:str, exception:bool=False)->str:
    """
    Get location using https://freegeoip.live/json
    :args:
        ip:str - IP address of node to get location of
    :params:
        location:str - (Latitude, Longitude)
    :return:
        location
    """
    status = True
    location = "0.0, 0.0"
    if find_spec('geocoder'):
        try: 
            myloc = geocoder.ip(ip)
        except Exception as e: 
            print('Error 1: %s' % e)
            status = False
        else: 
            try: 
                location = '%s, %s' % (myloc.latlng[0], myloc.latlng[1])
            except Exception as e: 
                print('Error 2: %s' % e)
                status = False

    if find_spec('geocoder') is None or status is False:
        if __validate_internet() is True:  
            try:
                r = requests.get("https://freegeoip.live/json/%s" % ip)
            except Exception as e:
                if exception is True:
                    print('Failed to execute request to get location by IP  (Error: %s)' % e)
            else:
                if int(r.status_code) == 200:
                    try:
                        output = r.json()
                    except Exception as e:
                        if exception is True:
                            print('Failed to convert info regarding IP as JSON (Error: %s)' % e)
                    else:
                        if output['latitude'] != '' and output['longitude'] != '':
                            location = '%s, %s' % (output['latitude'], output['longitude'])
                        elif exception is True:
                            print('Failed to extract latitude & longitude regarding IP %s' % ip)
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

    if 'default_dbms' in config:
        if 'table' in config:
            cluster['cluster']['table'] = __format_tables(config['default_dbms'], config['table'].split(','))
        else:
            cluster['cluster']['dbms'] = config['default_dbms']

    return cluster


def declare_node(config:dict, disable_location:bool=False, exception:bool=False)->dict:
    """
    Declare generic node based on config
    :args: 
        config:dict - config info
        location:bool - whether or to disbale (ie not add) location information when declaring policy
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
    
    if disable_location is False and 'location' not in config:
        node[config['node_type']]['loc'] = __get_location(ip=config['external_ip'], exception=exception)
    elif disable_location is False:
        node[config['node_type']]['loc'] = config['location']

    if config['node_type'] == 'operator':
        if 'cluster_id' in config:
            node[config['node_type']]['cluster'] = config['cluster_id']

        if 'default_dbms' in config:
            node[config['node_type']]['dbms'] = config['default_dbms']
            if 'table' in config and 'cluster_id' not in config:
                # if node is correlated to a cluster there's no need to specify tables within policy
                nodes = []
                for table in config['table'].split(','):
                    node[config['node_type']]['table'] = table
                    nodes.append(node)
                node = nodes

    return node

