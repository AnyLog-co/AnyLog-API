import os 

def postgres(conn:str, exception:bool=False)->bool: 
    """
    Deploy Postgres instance
    :args: 
        conn:str - connection to AnyLog
        exception:bool - whether or not to print exception
    :params: 
        status:bool
        psql_user:str - from conn extract username
        psql_pass:str - from conn extract password
        cmd:str - Docker command to execute
    :return: 
        status
    """
    status = True
    psql_user = conn.split('@')[0]
    psql_pass = conn.split(':')[1]
    cmd = 'docker run -d --network host --name anylog-psql -e POSTGRES_USER=%s -e POSTGRES_PASSWORD=%s -v pgdata:/var/lib/postgresql/data postgres:latest'

    try: 
        os.system(cmd % (psql_user, psql_pass)) 
    except Exception as e: 
        if exception == True: 
            print('Failed to deploy Postgres instance (Error: %s)' % e)
        status = False

    return status

def grafana(exception:bool=False)->bool: 
    """
    Deploy Grafana instance
    :args: 
        exception:bool - whether or not to print exception
    :params: 
        status:bool
        cmd:str - Docker command to execute
    :return:
        status
    """
    status = True 
    cmd = 'docker run -d -p 3000:3000 --name=grafana -v grafana-data:/var/lib/grafana -v grafana-log:/var/log/grafana -v grafana-config:/etc/grafana -e "GF_INSTALL_PLUGINS=simpod-json-datasource,grafana-worldmap-panel" grafana/grafana'

    try: 
        os.system(cmd)
    except Exception as e: 
        if exception == True: 
            print('Failed to deploy Grafana instance (Error: %s)' % e)
        status = False

    return status 

def anylog(config:dict, exception:bool=False)->bool: 
    """
    Deploy AnyLog instance 
    :args: 
        config:str - AnyLog configuration
        exception:bool - whether or not to print exception
    :params: 
        status:bool
        cmd:str - Docker command to execute
    :return:
        status
    """
    status = True
    cmd = 'docker run --network host --name %s -e NODE_TYPE=rest -e ANYLOG_SERVER_PORT=%s -e ANYLOG_REST_PORT=%s -v %s-anylog:/app/AnyLog-Network/anylog:rw -v %s-blockchain:/app/AnyLog-Network/blockchain:rw    -v %s-data:/app/AnyLog-Network/data:rw -it oshadmon/anylog:predevelop'

    node_name   = 'new-node' 
    server_port = 2048 
    rest_port   = 2049 
    
    if 'node_name' in config:
        node_name = config['node_name']
    if 'anylog_server_port' in config: 
        server_port = config['anylog_server_port']
    if 'anylog_rest_port' in config: 
        rest_port = config['anylog_rest_port']

    cmd = cmd % (node_name, server_port, rest_port, node_name, node_name, node_name) 

    if 'anylog_broker_port' in config: 
        cmd = cmd.replace('ANYLOG_REST_PORT=%s' % rest_port, 'ANYLOG_REST_PORT=%s -e ANYLOG_BROKER_PORT=%s' % (rest_port, config['anylog_broker_port'])) 

    try: 
        os.system(cmd)
    except Exception as e: 
        if exception == True: 
            print('Failed to deploy Grafana instance (Error: %s)' % e)
        status = False

    return status 


