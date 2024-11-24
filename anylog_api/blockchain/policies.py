"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""


def create_cluster_policy(name:str, owner:str, db_name:str=None, table:str=None, parent:str=None):
    """
    Declare cluster policy
    :args:
        name:str - cluster name
        owner:str - company name / cluster owner
    :optional-args:  if specified, then the cluster will only work against given database and/or table OR associated with a parent cluster
        db_name:str - specific database name
        table:str - specific table name
        parent:str - cluster parent ID
    :params:
        node_policy
    :return:
        node_policy
    """
    cluster_policy = {
        "cluster": {
            "name": name,
            "company": owner
        }
    }
    if db_name and parent:
        cluster_policy['cluster']['parent'] = parent
    if db_name and table:
        cluster_policy['cluster']['table'] = [
            {
                "dbms": db_name,
                "table": table
            }
        ]
    elif db_name:
        cluster_policy['cluster']['dbms'] = db_name
    return cluster_policy


def create_node_policy(node_type:str, node_name:str, owner:str, ip:str, anylog_server_port:int, anylog_rest_port:str,
                       local_ip:str=None, anylog_broker_port:int=None, cluster_id:str=None, is_main:bool=False,
                       location:dict=None, other_params:dict=None, scripts:list=None):
    """
    Declare dictionary object which will be used as the policy for the node
    :sample-policy:
        {'operator' : {
            'name' : 'syslog-operator2',
            'company' : 'AnyLog Co.',
            'ip' : '172.105.219.25',
            'local_ip' : '172.105.219.25',
            'port' : 32148,
            'rest_port' : 32149,
            'broker_port' : 32150,
            'main' : False,
            'cluster' : '2957ab8c837c52d9160c4b60041cbf08',
            'loc' : '35.6895,139.6917',
            'country' : 'JP',
            'city' : 'Tokyo',
        }}
    :args:
        node_type:str - node type (ex. master, operator, query)
        node_name:str - node name
        owner:str - owner / company that the node is associated with
        ip:str - (external) IP of the node
        local_ip:str - (local) Ip of the node
        anylog_server_port:int - TCP port value
        anylog_rest_port:int - REST port value
        anylog_broker_port:int - Message broker port
        cluster_id:str - for Operator, the cluster ID
        is_main:bool - for operator whether the node is a primary or secondary
        location:dict - geolocation of the node
            loc:str - coordinates
            country:str
            city:str
            ...
        other_params:dict - dictionary of non-"default" params
        scripts:list - any commands to be executed as part of the policy
    :params:
        node_type:dict - generated AnyLog policy
    :return:
        node_policy
    """
    node_policy = {
        node_type: {
            "name": node_name,
            "company": owner,
            "ip": ip,
            "port": int(anylog_server_port),
            "rest_port": int(anylog_rest_port)
        }
    }

    if local_ip:
        node_policy[node_type]['local_ip'] = local_ip
    if anylog_broker_port:
        node_policy[node_type]['broker_port'] = int(anylog_broker_port)
    if node_type == 'operator':
        node_policy[node_type]['main'] = is_main
        if cluster_id:
            node_policy[node_type]['cluster'] = cluster_id
        elif not cluster_id:
            raise ValueError('Error: Unable to create operator policy, must have a cluster to associate with')
    if location:
        for loc in location:
            node_policy[node_type][loc] = location[loc]
    if other_params:
        for param in other_params:
            node_policy[node_type][param] = other_params[param]
    if scripts:
        node_policy[node_type]['script'] = scripts

    return node_policy


def table_policy(db_name:str, table_name:str, create_stmt:str):
    """
    Create table policy
    :sample policy:
     {'table' : {'name' : 'people_counter',
             'dbms' : 'edgex',
             'create' : 'CREATE TABLE IF NOT EXISTS people_counter(  row_id SERIAL PRIMAR'
                        'Y KEY,  insert_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),  tsd_'
                        'name CHAR(3),  tsd_id INT,  timestamp TIMESTAMP not null default'
                        ' now(),  start_ts timestamp,  end_ts timestamp,  file varchar,  '
                        'people_count int,  confidence float ); CREATE INDEX people_count'
                        'er_end_ts_index ON people_counter(end_ts); CREATE INDEX people_c'
                        'ounter_start_ts_index ON people_counter(start_ts); CREATE INDEX '
                        'people_counter_timestamp_index ON people_counter(timestamp); CRE'
                        'ATE INDEX people_counter_tsd_index ON people_counter(tsd_name, t'
                        'sd_id); CREATE INDEX people_counter_insert_timestamp_index ON pe'
                        'ople_counter(insert_timestamp);',
             'source' : 'Processing JSON file',
             'id' : 'd88b70f6c5ea6f104dbbe36436f7ba6a',
             'date' : '2024-11-04T05:20:44.190559Z',
             'ledger' : 'global'}},
    :args:
        db_name:str - logical database whee table exists
        table_name:str - table name
        create_stmt:str - create table statement
    :params:
        new_policy:dict - generated policy
    :return:
        new_policy
    """
    new_policy = {
        "name": table_name,
        "dbms": db_name,
        "create": create_stmt
    }

    return new_policy


def generic_policy(policy_type:str, policy_name:str, owner:str, scripts:list=None, policy_id:str=None, **kwargs)->dict:
    """
    Allow user to generate  unique policy - an example is config and schedule policies
    :sample policy:
        {'schedule': {
            'id' : 'generic-schedule-policy',
            'name' : 'Generic Monitoring Schedule',
            'script' : ['schedule name = monitoring_ips and time=300 seconds and task mon'
                                 'itoring_ips = blockchain get query bring.ip_port',
                            'if !store_monitoring == true and !node_type == operator then pro'
                                 'cess !anylog_path/deployment-scripts/demo-scripts/monitoring_tab'
                                 'le_policy.al',
                            'if !store_monitoring == true and !node_type != operator then sch'
                                 'edule name=operator_monitoring_ips and time=300 seconds and task'
                                 ' if not !operator_monitoring_ip then operator_monitoring_ip = bl'
                                 'ockchain get operator bring.first [*][ip] : [*][port]',
                            'schedule name = get_stats and time=30 seconds and task node_insi'
                                 'ght = get stats where service = operator and topic = summary  an'
                                 'd format = json',
                            'schedule name = get_timestamp and time=30 seconds and task node_'
                                 'insight[timestamp] = get datetime local now()',
                            'schedule name = set_node_type and time=30 seconds and task set n'
                                 'ode_insight[node type] = !node_type',
                            'schedule name = get_disk_space and time=30 seconds and task disk'
                                 '_space = get disk percentage .',
                            'schedule name = get_cpu_percent and time = 30 seconds task cpu_p'
                                 'ercent = get node info cpu_percent',
                            'schedule name = get_packets_recv and time = 30 seconds task pack'
                                 'ets_recv = get node info net_io_counters packets_recv',
                            'schedule name = get_packets_sent and time = 30 seconds task pack'
                                 'ets_sent = get node info net_io_counters packets_sent',
                            'schedule name = disk_space   and time = 30 seconds task if !disk'
                                 '_space   then node_insight[Free Space Percent] = !disk_space.flo'
                                 'at',
                            'schedule name = cpu_percent  and time = 30 seconds task if !cpu_'
                                 'percent  then node_insight[CPU Percent] = !cpu_percent.float',
                            'schedule name = packets_recv and time = 30 seconds task if !pack'
                                 'ets_recv then node_insight[Packets Recv] = !packets_recv.int',
                            'schedule name = packets_sent and time = 30 seconds task if !pack'
                                 'ets_sent then node_insight[Packets Sent] = !packets_sent.int',
                            'schedule name = errin and time = 30 seconds task errin = get nod'
                                 'e info net_io_counters errin',
                            'schedule name = errout and time = 30 seconds task errout = get n'
                                 'ode info net_io_counters errout',
                            'schedule name = get_error_count and time = 30 seconds task if !e'
                                 'rrin and !errout then error_count = python int(!errin) + int(!er'
                                 'rout)',
                            'schedule name = error_count and time = 30 seconds task if !error'
                                 '_count then node_insight[Network Error] = !error_count.int',
                            'schedule name = local_monitor_node and time = 30 seconds task mo'
                                 'nitor operators where info = !node_insight',
                            'schedule name = monitor_node and time = 30 seconds task if !moni'
                                 'toring_ips then run client (!monitoring_ips) monitor operators w'
                                 'here info = !node_insight',
                            'schedule name = clean_status and time = 30 seconds task node_ins'
                                 'ight[status]='Active'',
                            'if !store_monitoring == true and !node_type == operator then sch'
                                 'edule name = operator_monitor_node and time = 30 seconds task st'
                                 'ream !node_insight where dbms=monitoring and table=node_insight',
                            'if !store_monitoring == true and !node_type != operator then sch'
                                 'edule name = operator_monitor_node and time = 30 seconds task if'
                                 ' !operator_monitoring_ip then run client (!operator_monitoring_i'
                                 'p) stream !node_insight  where dbms=monitoring and table=node_in'
                                 'sight'],
                }}
    :args:
        policy_type:str - policy type
        policy_name:str - policy name
        owner:str - policy owner (company name)
        scripts:list - list of commands / scripts to run
        policy_id:str - policy ID (note, no 2 policies can have the same ID)
        **kwargs - user define policy values
    :params:
        new_policy:dict - generated policy
    :return:
        new_policy
    """
    new_policy = {
        policy_type: {
            'name': policy_name,
            'company': owner,
            "script": scripts,
            "id": policy_id
        }
    }

    if not scripts:
        del new_policy[policy_type]['script']
    if not policy_id:
        del new_policy[policy_type]['id']
    if kwargs:
        new_policy[policy_type] = {**new_policy[policy_type], **kwargs}

    return new_policy
