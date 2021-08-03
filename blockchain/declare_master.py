def declare_master(conn:str, config:dict): 
    """
    Declare master node based on config
    :args: 
        conn:str - REST connection information
        config:dict - config info
     """
     declare_statement = {
         'name':      config['node_name'], 
         'ip':        config['external_ip'],
         'local_ip':  config['ip'],
         'port':      config['anylog_server_port'],
         'rest_port': config['anylog_rest_port'], 
     }
     if 'hostname' in  config: 
         declare_statement['hostname'] = config['hostname']
     if 'location' in config: 
         declare_statement['location'] = config['location'] 

     
