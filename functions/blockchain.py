import os
import sys 

rest_dir = os.path.expandvars(os.path.expanduser('$HOME/AnyLog-API/rest')) 
sys.path.insert(om rest_dir) 

def __convert_table(default_dbms:str, tables:str, cluster:bool=True)->str:
    """
    Given a list of tables, if cluster is enabled convert to proper format
    :args: 
       default_dbms:str - database name 
       tables:str - comman seperated list of tables 
       cluster:bool - whether to format tables for cluster or operator
    :param: 
        tables_list:list - formatted tables list 
    :return: 
        tables_list
    """
    tables = tables.split(',') # convert tables into list 
    tables_list = []
    if cluster == True: 
        for table in tables:
            tables_list.append({"name": "%s" % table, "dbms": "%s" % default_dbms})
        return tables_list
    return tables 
 

def pull_json(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True, master_node:str="!master_node")->bool: 
    """
    Pull to blockchain 
    :args:
        conn:str - REST connection information
        timeout:float - REST timeout 
        auth:tuple - REST authentication 
        exception:bool - print exception messages
        master_node:str - master node connection information
    :param: 
        status:bool
    :return:
        status 
    """
    cmd = "blockchain pull to json !blockchain_file" 
    if master_node != None: 
        cmd = "run client (%s) %s" % (master_node, cmd.replace("!blockchain_file", "!!blockchain_file") )
    status = rest.post(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    if status == True and master_node != None: 
        cmd = "run client (%s) file get !!blockchain_file !blockchain_file" % master_node 
        status = rest.post(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    return status 

def get_policy(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True, policy:str="*", where:str=None, bring:str=None)->list: 
    """
    Query blockchain 
    :args:
        conn:str - REST connection information
        timeout:float - REST timeout 
        auth:tuple - REST authentication 
        exception:bool - print exception messages
        policy:str - policy to get from blockchain 
        where:str - WHERE condition for exttracting policy(ies) from blockchain
        bring:str - BRING information format from policies
    :param: 
        output - raw data from query 
        cmd:str - command to execute
    :return:
        output 
    """
    cmd = "blockchain get %s" % policy
    if where != None: 
        cmd += " where %s" % where 
    if bring != None: 
        cmd += " bring %s" % bring
    print(cmd)
    output = rest.get(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception) 
    return output 

def declare_policy(conn:str, anylog_params:dict, timeout:float=10, auth:tuple=None, exception:bool=True)->bool: 
    """
    Declare policy to blockchain
    :args:
        conn:str - REST connection information
        timeout:float - REST timeout 
        auth:tuple - REST authentication 
        exception:bool - print exception messages
        anylog_params:dict - AnyLog parameters   
    :param: 
        status:bool 
        policy:dict - generic declartion of policy 
    :return: 
        status 
    :base JSON: 
    {"publisher" : {
        "hostname": !hostname,
        "name": !node_name,
        "company": !company_name, 
        "ip" : !external_ip,
        "port" : !anylog_server_port.int,
        "rest_port": !anylog_rest_port.int, 
        "loc": !loc
        }
    }
    """
    status = True 
    if 'node_type' in anylog_params:
        policy = {anylog_params['node_type']: {}} 
    else: 
        policy = {'policy': {}}
    key = list(policy.keys())[0]
    
    if 'hostname' in anylog_params: 
        policy[key]['hostname'] = anylog_params['hostname']
    if 'name' in anylog_params: 
        policy[key]['name'] = anylog_params['name']
    if 'external_ip' in anylog_params: 
        policy[key]['ip'] = anylog_params['external_ip']
    if 'ip' in anylog_params and 'ip' not in policy: 
        policy[key]['ip'] = anylog_params['ip']
    if 'ip' in anylog_params:
        policy[key]['local_ip'] = anylog_params['ip']
    if 'anylog_server_port' in anylog_params: 
        try: 
            policy[key]['port'] = int(anylog_params['anylog_server_port']) 
        except: 
            policy[key]['port'] = anylog_params['anylog_server_port'] 
    if 'anylog_rest_port' in anylog_params: 
        try: 
            policy[key]['rest_port'] = int(anylog_params['anylog_rest_port']) 
        except: 
            policy[key]['rest_port'] = anylog_params['anylog_rest_port'] 
    if 'company' in anylog_params: 
        policy[key]['company'] = anylog_params['company'] 
    if 'loc' in anylog_params: 
        policy[key]['loc'] = anylog_params['loc'] 
    elif 'loc' not in anylog_params and key in ['master','operator', 'publisher', 'query']: 
        policy[key]['loc'] = rest.get_location() 
    
    # Operator specific params 
    if 'default_dbms' not in anylog_params: 
        anylog_params['default_dbms'] = None
    if 'db_type' in anylog_params: 
        policy[key]['db_type'] = anylog_params['db_type'] 
    if 'cluster_id' in anylog_params:
        policy[key]['cluster'] = anylog_params['cluster_id']
    elif 'cluster_id' not in anylog_params and 'table' in anylog_params: 
        policy[key]['table'] = __convert_table(default_dbms=anylog_params['default_dbms'], tables=anylog_params['table'], cluster=False) 
    if 'member_id' in anylog_params: 
        policy[key]['member'] = anylog_params['member_id']

    status = rest.post_policy(conn=conn, policy=policy, timeout=timeout, auth=auth, exception=exception)
    return status 


def declare_cluster(conn:str, anylog_params:dict, timeout:float=10, auth:tuple=None, exception:bool=True)->bool: 
    """
    Declare policy to blockchain
    :args:
        conn:str - REST connection information
        timeout:float - REST timeout 
        auth:tuple - REST authentication 
        exception:bool - print exception messages
        anylog_params:dict - AnyLog parameters   
    :param: 
        status:bool 
        policy:dict - generic declartion of policy 
    :return: 
        status 
    :base JSON: 
    {"cluster": {
        "company": !company_name,
        "name": !cluster_name,
        "table": !table
    }}
    """
    status = True 
    if 'node_type' in anylog_params:
        policy = {'cluster': {}} 
    else: 
        policy = {'policy': {}}
    key = list(policy.keys())[0]
    if 'cluster_name' in anylog_params:
        policy[key]['name'] = anylog_params['cluster_name'] 
    if 'company_name' in anylog_params: 
        policy[key]['company'] = anylog_params['company_name']
    if 'table' in anylog_params: 
        policy[key]['table'] = __convert_table(default_dbms=anylog_params['default_dbms'], tables=anylog_params['table'], cluster=True) 

    status = rest.post_policy(conn=conn, policy=policy, timeout=timeout, auth=auth, exception=exception)
    return status 


