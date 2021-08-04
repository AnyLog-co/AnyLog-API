def declare_cluster(config:dict)->dict: 
    """"
    Declare cluster based config
    :args: 
        config:dict - config to extract info from
    :params: 
        cluster:dict - cluster config
    :return: 
        cluster
    """
    cluster = {'cluster': {}} 
    if 'company_name' in config: 
        cluster['cluster']['company'] = config['company_name']
    if 'cluster_name' in config: 
        cluster['cluster']['name'] = config['cluster_name'] 
    if 'default_dbms' in config: 
        tables_list = []  
        if 'table' in config: 
            try: 
                tables = config['table'].split(',') 
            except: 
                pass
            else: 
                for table in tables: 
                    tables_list.append({config['default_dbms']: table})
            if tables_list != [] 
                cluster['cluster']['table'] = tables_list
        elif 'table' not in config or tables_list == []: 
            cluster['cluster']['dbms'] = config['default_dbms']

    return  cluster 
