def create_generic_policy(policy_type:str, name:str, company:str, hostname:str, external_ip:str, local_ip:str,
                          anylog_server_port:int, anylog_rest_port:int, location:str="Unknown", country:str="Unknown",
                          state:str="Unknown", city:str="Unknown")->dict:
    """
    Create policy for Master, Publisher or Query
    :sample-policy:
        {
            'publisher' : {
              'hostname' : 'al-live-publisher',
              'name' : 'anylog-publisher-node',
              'ip' : '172.104.180.110',
              'local_ip' : '172.104.180.110',
              'company' : 'AnyLog',
              'port' : 32248,
              'rest_port' : 32249,
              'loc' : '1.2897,103.8501',
              'country' : 'SG',
              'state' : 'Singapore',
              'city' : 'Singapore',
            }
        }
    :args:
        policy_type:str - policy type (master, publisher or query)
        name:str - policy name
        company:str - company associated with policy
        hostname:str - host of node policy resides on
        external_ip:str / local_ip:int - IP information of the machine
        anylog_server_port:int / anylog_rest_port:int - TCP + REST ports
        loc:str / country:str / state:str / city - location of the machine
    :params:
        policy:dict - completed param
    :return:
        policy
    """
    policy = {
        policy_type: {
            "name": name,
            "company": company,
            "hostname": hostname,
            "ip": external_ip,
            "local_ip": local_ip,
            "port": anylog_server_port,
            "rest_port": anylog_rest_port
        }
    }
    if location is not None:
        policy[policy_type]['loc'] = location
    if country is not None:
        policy[policy_type]['country'] = country
    if state is not None:
        policy[policy_type]['state'] = state
    if city is not None:
        policy[policy_type]['city'] = city

    return policy


def create_cluster_policy(name:str, company:str, db_name:str=None)->dict:
    """
    Create a policy for cluster
    :sample-policy:
        {
            'cluster' : {
              'company' : 'Lit San Leandro',
              'dbms' : 'litsanleandro',
              'name' : 'litsanleandro-cluster1'
            }
        }
    :args:
        name:str - cluster name
        company:str - company associated with cluster
        db_name:str - db associated with cluster
    :params:
        policy:dict - cluster policy
    :return:
        policy
    """
    policy = {
        'cluster': {
            'name': name,
            'company': company
        }
    }
    if db_name is not None:
        policy['cluster']['dbms'] = db_name

    return policy


def create_operator_policy(name:str, company:str, hostname:str, external_ip:str, local_ip:str, anylog_server_port:int,
                           anylog_rest_port:int, cluster_id:str=None, member:int=None, location:str="Unknown",
                           country:str="Unknown", state:str="Unknown", city:str="Unknown")->dict:
    """
    Create an Operator policy
    :sample-policy:
        {
            'operator' : {
              'hostname' : 'al-live-operator1',
              'name' : 'anylog-cluster1-operator1',
              'ip' : '139.162.126.241',
              'local_ip' : '139.162.126.241',
              'company' : 'Lit San Leandro',
              'port' : 32148,
              'rest_port' : 32149,
              'cluster' : '0015392622f3eaac70eafa4311fc2338',
              'member' : 12,
              'loc' : '35.6895,139.6917',
              'country' : 'JP',
              'state' : 'Tokyo',
              'city' : 'Tokyo',
            }
        }
    :args:
        policy_type:str - policy type (master, publisher or query)
        name:str - policy name
        company:str - company associated with policy
        hostname:str - host of node policy resides on
        external_ip:str / local_ip:int - IP information of the machine
        anylog_server_port:int / anylog_rest_port:int - TCP + REST ports
        cluster_id:str - ID of cluster operator is associated with
        member:int - operator member ID
        loc:str / country:str / state:str / city - location of the machine
    :params:
        policy:dict - cluster policy
    :return:
        policy
    """
    policy = create_generic_policy(policy_type='operator', name=name, company=company, hostname=hostname,
                                   external_ip=external_ip, local_ip=local_ip, anylog_server_port=anylog_server_port,
                                   anylog_rest_port=anylog_rest_port, location=location, country=country, state=state,
                                   city=city)

    if cluster_id is not None:
        policy['operator']['cluster'] = cluster_id
    if member is not None:
        policy['operator']['member'] = member

    return policy
