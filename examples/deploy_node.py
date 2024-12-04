import json
from anylog_api.anylog_api import AnyLogAPI


def __create_database_connection(db_name:str, db_type:str, db_user:str=None, db_passwwd:str=None, db_ip:str=None,
                                 db_port:int=None, memory:bool=False):
    """
    create command for connection to database
    :args:
        db_name:str - logical database name
        db_type:str - database type
        db_user:str - database user credential
        db_passwd:str - database password credential
        db_ip:str - database IP address
        db_port:int - database port value
        memory:bool - run database in memory
    :params:
        command:str - generated `connect dbms` command
    :return:
        command
    """
    command = f"connect dbms {db_name} where type={db_type}"
    if db_type == "sqlite" and memory is True:
        command += f" and memory=true"
    if db_type != 'sqlite':
        if db_user:
            command += f" and ip={db_ip}"
        if db_port:
            command += f" and port={db_port}"
        if db_user:
            command += f" and user={db_user}"
        if db_passwwd:
            command += f" and password={db_passwwd}"

    return command


def get_policy_id(conn:AnyLogAPI, policy_type:str, policy_name:str, company_name:str):
    policy_id = None
    command = f"blockchain get {policy_type} where name={policy_name}"

    output = conn.execute_get(command=command, destination=None, view_help=False)
    if output and 'id' in output[0][list(output[0].keys())[0]]:
        policy_id = output[0][list(output[0].keys())[0]]['id']
    return policy_id

def declare_policy(conn:AnyLogAPI, policy:dict, ledger_conn:str):
    """
    Declare policy on blockchain
    :args:
        conn:anylog_api.AnyLogAPI - connection to AnyLog/EdgeLake
        policy:dict - generated policy
        ledger_conn:str - master node / blockchain platform connection information
    :params:
        command:str - generated AnyLog command
        new_policy:str - generated policy to be sent into AnyLog/EdgeLake
    """
    command = f"blockchain insert where policy=!new_policy and local=true and master={ledger_conn}"
    new_policy = f"<new_policy={json.dumps(policy)}>"
    conn.execute_post(command=command, payload=new_policy, topic=None, destination=None, view_help=False)


def cluster_node(cluster_name:str, company_name:str):
    new_policy = {
        "cluster": {
            "name": cluster_name,
            "company": company_name
        }
    }

    return new_policy


def node_policy(node_type:str, node_name:str, company_name:str, external_ip:str, local_ip:str, anylog_server_port:int,
                anylog_rest_port:int, cluster_policy:str=None):
    new_policy =  {
        node_type: {
            "name": node_name,
            "company": company_name,
            "ip": external_ip,
            "local_ip": local_ip,
            "port": anylog_server_port,
            "rest_port": anylog_rest_port
        }
    }
    if cluster_policy:
        new_policy[node_type]['cluster'] = cluster_policy
    return new_policy


def deploy_node(anylog_conn:AnyLogAPI, params:dict):
    """
    Declare basic services for node deploymnet
        - source paths
        - database and tables
        - blockchain sync
    :args:
        anylog_conn:AnyLogAPI - connection to AnyLog/EdgeLake
        params:dict - configurations for declaring set params
    :params:
        cmd:str - command to execute via POST
        anylog_path:str - root path for anylog
        db_name:str - logical database name
        db_type:str - database type
        db_user:str - database user credential
        db_passwd:str - database password credential
        db_ip:str - database IP address
        db_port:int - database port value
        memory:bool - run database in memory
        blockchain_source:str - blockchain source
        blockchain_destination:str - location to store blockchain locally
        ledger_conn:str - TCP connection information for master node
        blockchain_sync:str - how often to sync blockchain
    """
    # set source path(s)
    anylog_path = '/root'
    if 'anylog_path' in params:
        anylog_path = params['anylog_path']
    elif 'edgelake_path' in params:
        anylog_path = params['edgelake_path']
    for cmd in [f'set anylog home {anylog_path}', f'create work directories', 'run scheduler 1']:
        anylog_conn.execute_post(command=cmd, payload=None, topic=None, destination=None, view_help=False)


    # connect database(s)
    db_name = None
    if 'default_dbms' in params and params['node_type'] == 'operator':
        db_name = params['default_dbms']
    elif params['node_type'] == 'master':
        db_name = 'blockchain'

    db_type = params['db_type'] if 'db_type' in params else 'sqlite'
    db_user = params['db_user'] if 'db_user' in params else None
    db_passwd = params['db_passwd'] if 'db_passwd' in params else None
    db_ip = params['db_ip'] if 'db_ip' in params else None
    db_port = params['db_port'] if 'db_port' in params else None
    system_query = params['system_query'] if 'system_query' in params else False
    memory = params['memory'] if 'memory' in params else False


    if db_name:
        cmd = __create_database_connection(db_name=db_name, db_type=db_type, db_user=db_user, db_passwwd=db_passwd, db_ip=db_ip, db_port=db_port)
        anylog_conn.execute_post(command=cmd, payload=None, topic=None, destination=None, view_help=False)
        if db_name == 'blockchain':
            cmd = f'create table ledger where dbms={db_name}'
            anylog_conn.execute_post(command=cmd, payload=None, topic=None, destination=None, view_help=False)
    if params['db_type'] in ['operator', 'publisher']:
        cmd = __create_database_connection(db_name='almgm', db_type=db_type, db_user=db_user, db_passwwd=db_passwd, db_ip=db_ip, db_port=db_port, memory=False)
        anylog_conn.execute_post(command=cmd, payload=None, topic=None, destination=None, view_help=False)
        cmd = 'create table tsd_info where dbms=almgm'
        anylog_conn.execute_post(command=cmd, payload=None, topic=None, destination=None, view_help=False)
    if system_query is True:
        cmd = __create_database_connection(db_name='system_query', db_type=db_type, db_user=db_user, db_passwwd=db_passwd, db_ip=db_ip, db_port=db_port, memory=memory)
        anylog_conn.execute_post(command=cmd, payload=None, topic=None, destination=None, view_help=False)

    # blockchain sync
    blockchain_source = params['blockchain_source'] if 'blockchain_source' in params else 'master'
    blockchain_destination = params['blockchain_destination'] if 'blockchain_destination' in params else 'file'
    ledger_conn = params['ledger_conn'] if 'ledger_conn' in params else '127.0.0.1:32048'
    blockchain_sync = params['sync_time'] if 'sync_time' in params else '30 seconds'

    cmd = f"run blockchain sync where source={blockchain_source} and time={blockchain_sync} and dest={blockchain_destination} and connection={ledger_conn}"
    anylog_conn.execute_post(command=cmd, payload=None, topic=None, destination=None, view_help=False)
