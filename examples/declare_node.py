import json
import anylog_api.anylog_api as anylog_api



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

def generic_node(params:dict)->dict:
    """
    Create the base for a given (node) policy
    :sample-policy:
    {
      "master" : {
        "name" : "anylog-master",
        "company" : "New Company",
        "ip" : "73.202.142.172",
        "local_ip" : "10.0.0.228",
        "rest_ip" : "10.0.0.228",
        "port" : 2048,
        "rest_port" : 2148,
        "tcp_bind" : "true",
        "rest_bind" : "true",
        "script" : [
            "connect dbms blockchain where type=sqlite", "create table ledger where dbms=blockchain",
            "connect dbms system_query where type=sqlite and memory=true",
            "run scheduler 1",
            "run blockchain sync where source=master and time=30 second and dest=file and connection=10.0.0.228:2048"
        ]
      }
    }
    :args:
        params:dict - User defined params
    :params:
        new_policy:dict - generated policy
    :return:
        new_policy
    """
    new_policy = {
        params['node_type']: {
            "name": params['node_name'],
            "company": params['company_name'],
            "ip": params['external_ip'],
        }
    }
    # IP address for TCP
    new_policy[params['node_type']]['local_ip'] =  params['overlay_ip'] if 'overlay_ip' in params else params['ip']

    if 'rest_bind' in params and params['rest_bind'] is True:
        new_policy[params['node_type']]['rest_ip'] = params['overlay_ip'] if 'overlay_ip' in params else params['ip']
    if 'broker_bind' in params and 'anylog_broker_port' in params:
        new_policy[params['node_type']]['broker_ip'] = params['overlay_ip'] if 'overlay_ip' in params else params['ip']

    new_policy[params['node_type']]['port'] = params['anylog_server_port']
    new_policy[params['node_type']]['rest_port'] = params['anylog_rest_port']
    if 'anylog_broker_port' in params:
        new_policy[params['node_type']]['broker_port'] = params['anylog_broker_port']

    new_policy[params['node_type']]['tcp_bind'] = str(params['tcp_bind']).lower() if 'tcp_bind' in params else "false"
    new_policy[params['node_type']]['rest_bind'] = str(params['rest_bind']).lower() if 'rest_bind' in params else "false"
    if 'anylog_broker_port' in params:
        new_policy[params['node_type']]['broker_bind'] = str(params['broker_bind']).str() if 'broker_bind' in params else False

    return new_policy


def create_scripts(params:dict)->list:
    """
    Based on params create (basic) scripts for deploying a node
    :args:
        params:dict - User defined params
    :params:
        scripts:list - list of command to execute as part of the policy
        db_name:str - logical database name
        db_type:str - database type
        db_user:str - database user credential
        db_passwd:str - database password credential
        db_ip:str - database IP address
        db_port:int - database port value
        system_query:str - whether to deploy system_query database
        memory:bool - run database in memory
        source:str - blockchain master / network as source
        blockchain_sync:str - sync time
        blockchain_destination:str - local location of storing the blockchain (file)
       ledger_conn:str - ledger connection information
    """
    scripts = []

    db_name = None
    if 'default_dbms' in params and params['node_type'] == 'operator':
        db_name = params['default_dbms']
    elif params['node_type'] == 'master':
        db_name = 'blockchain'

    db_type = params['db_type']
    db_user = params['db_user'] if 'db_user' in params else None
    db_passwd = params['db_passwd'] if 'db_passwd' in params else None
    db_ip = params['db_ip'] if 'db_ip' in params else None
    db_port = params['db_port'] if 'db_port' in params else None
    system_query = params['system_query'] if 'system_query' in params else False
    memory = params['memory'] if 'memory' in params else False

    if db_name:
        scripts.append(__create_database_connection(db_name=db_name, db_type=db_type, db_user=db_user,
                                                    db_passwwd=db_passwd, db_ip=db_ip, db_port=db_port))
        if db_name == 'blockchain':
            scripts.append(f'create table ledger where dbms={db_name}')
    if params['db_type'] in ['operator', 'publisher']:
        scripts.append(__create_database_connection(db_name='almgm', db_type=db_type, db_user=db_user,
                                                    db_passwwd=db_passwd, db_ip=db_ip, db_port=db_port, memory=False))
        scripts.append('create table tsd_info where dbms=almgm')
    if system_query is True:
        scripts.append(__create_database_connection(db_name='system_query', db_type=db_type, db_user=db_user,
                                                    db_passwwd=db_passwd, db_ip=db_ip, db_port=db_port, memory=memory))
    scripts.append('run scheduler 1')

    source = params['blockchain_source'] if 'blockchain_source' in params else 'master'
    blockchain_sync = params['sync_time'] if 'sync_time' in params else '30 seconds'
    blockchain_destination = params['blockchain_destination'] if 'blockchain_destination' in params else 'file'
    ledger_conn = params['ledger_conn'] if 'ledger_conn' in params else '127.0.0.1:32048'
    scripts.append(f"run blockchain sync where source={source} and time={blockchain_sync} and dest={blockchain_destination} and connection={ledger_conn}")

    return scripts


def check_policy(conn:anylog_api.AnyLogAPI, policy_type:str, policy_name:str):
    policy_id = None
    command = f"blockchain get {policy_type} where name={policy_name}"

    output = conn.execute_get(command=command, destination=None, view_help=False)
    if output and 'id' in output[0][list(output[0].keys())[0]]:
        policy_id = output[0][list(output[0].keys())[0]]['id']
    return policy_id

def declare_policy(conn:anylog_api.AnyLogAPI, policy:dict, ledger_conn:str):
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

def config_policy(conn:anylog_api.AnyLogAPI, policy_id:str):
    """
    Declare  node based on script / configs
    :args:
        conn:anylog_api.AnyLogAPI - connection to AnyLog/EdgeLake
        policy_id:str - policy to configure from
    :params:
        command:str - command to execute
    """
    command = f"config from policy where id={policy_id}"
    conn.execute_post(command=command, payload=None, topic=None, destination=None, view_help=False)
