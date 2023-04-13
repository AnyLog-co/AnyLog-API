import support


def generate_blockchain_get(policy_type:str, where_conditions:dict=None, bring_conditions:str=None,
                            bring_values:str=None, separator:str=None):
    """
    Generate `blockchain get` command based on params
    :args:
        policy_type:str - policy types to get
        where_conditions:dict - dictionary of WHERE conditions (ex. {"company": "New Company", "rest_port": 32049})
        bring_conditions:str - bring conditions (ex. table, table.unique)
        bring_values:str - values to bring (ex. [*][ip]:[*][port])
        separator:str - how to separate values (if using new-line then \\n)
    :params:
        command:str - generated blockchain get command
        policy_type:list - converted policy_type to list of policy types
        where_stmt:str - built where condition based on where_conditions
        bring_stmt:str - built bring conditions
    :return:
        command
    """
    command = "blockchain get ("
    policy_type = policy_type.strip().split(",")
    for policy in policy_type:
        command += policy.strip()
        if policy != policy_type[-1]:
            command += ", "
        else:
            command += ")"

    if where_conditions is not None:
        where_stmt = "where"
        for key in where_conditions:
            if isinstance(where_conditions[key], str) and " " in where_conditions[key]:
                where_stmt += f' {key}="{where_conditions[key]}"'
            else:
                where_stmt += f" {key}={where_conditions[key]}"
            if key != list(where_conditions.keys())[-1]:
                where_stmt += " and"
        command += " " + where_stmt

    if bring_conditions is not None or bring_values is not None:
        bring_stmt = "bring"
        if bring_conditions is not None:
            bring_stmt += f".{bring_conditions}"
        if bring_values is not None:
            bring_stmt += f" {bring_values}"
        command += " " + bring_stmt
        if separator is not None:
            command += f" separator={separator}"

    return command


def generate_blockchain_insert(local_publish:bool=True, platform:str=None, ledger_conn:str=None):
    """
    Generate blockchain insert statement
    :sample command:
        blockchain insert where policy = !policy and local = true and master = !master_node
        blockchain insert where policy = !policy and local = true and blockchain = ethereum
    :args:
        local_publish:bool - A true/false value to determine an update to the local copy of the ledger
        platform:str - connected blockchain platform
        ledger_conn:str - The IP and Port value of a master node
    :params:
        command:str - generated blockchain insert command
    :return:
        command
    """
    command = 'blockchain insert where policy=!new_policy'
    if local_publish is False:
        command += " and local=false"
    else:
        command += " and local=true"

    if platform in ['ethereum', 'eos', 'jasmy']:
        command += f" and blockchain={platform}"

    if ledger_conn is not None:
        command += f' and master={ledger_conn}'

    return command


def node_policy(policy_type:str, name:str, company:str, external_ip:str, local_ip:str, anylog_server_port:int,
                anylog_rest_port:int, hostname:str=None, member:int=None, cluster_id:str=None,
                anylog_broker_port:int=None, location:str="Unknown", country:str="Unknown", state:str="Unknown",
                city:str="Unknown", exception:bool=False):
    """
    Generate policy for:
        - master
        - operator
        - publisher
        - query
    :sample policy:
        {"publisher": {
              "hostname": "al-live-publisher",
              "name": "anylog-publisher-node",
              "ip": "172.104.180.110",
              "local_ip": "172.104.180.110",
              "company": "AnyLog",
              "port": 32248,
              "rest_port": 32249,
              "loc": "1.2897,103.8501",
              "country": "SG",
              "state": "Singapore",
              "city": "Singapore",
              "id": "d2ef8f32b3d894f4d721275435e7d05d",
              "date": "2022-06-06T00:38:45.838582Z",
              "ledger": "global"
        }}
    :args:
        -- required
            policy_type:str - policy type (master, operator, publisher, query)
            name:str - policy name
            company:str - company policy is associated with
            external_ip:str - external IP of the physical node AnyLog is running on
            local_ip:str - local or internal IP of the physical node AnyLog is running on
            anylog_server_port:int - the TCP port for the node
            anylog_rest_port:int - the  REST port the node
        -- operator specific
            member:int - operator node ID (if not set autogenerated)
            cluster_id:str - ID of the cluster the operator is associated with
        -- optional
            hostname:str - name of the host AnyLog seats on
            anylog_broker_port:int - extend to have the broker port for a given node (if set)
            location:str - coordinate location of the physical node
            country:str - country where physical node is located
            state:str - state where physical node is located
            city:str - city where physical node is located
        exception:bool - whether to print exceptions
    :params:
        policy:dict - generated policy based on the given params
    :return:
        policy as JSON string
    """
    policy = {
        policy_type: {
            "name": name,
            "company": company,
            "ip": external_ip,
            "local_ip": local_ip,
            "port": anylog_server_port,
            "rest_port": anylog_rest_port,
        }
    }

    if hostname is not None:
        policy[policy_type]["hostname"] = hostname
    if policy_type == "operator":
        if member is not None:
            policy[policy_type]["member"] = member
        if cluster_id is not None:
            policy[policy_type]["cluster"] = cluster_id
    if anylog_broker_port is not None:
        policy[policy_type]["broker_port"] = anylog_broker_port
    if location is not None:
        policy[policy_type]["loc"] = location
    if country is not None:
        policy[policy_type]["country"] = country
    if state is not None:
        policy[policy_type]["state"] = state
    if city is not None:
        policy[policy_type]["city"] = city

    return support.json_dumps(content=policy, indent=0, exception=exception)


def cluster_policy(name:str, company:str, parent_cluster:str=None, db_name:str=None, table_name:str=None,
                   exception:bool=False):
    """
    Generate a cluster policy
    :sample cluster:
    {"cluster": {
        "company": "IOTech System",
        "dbms": "edgex",
        "name": "edgex-cluster2",
        "id": "0172634946c53e4c9bbede925182aa18",
        "date": "2023-01-12T21:35:10.388301Z",
        "status": "active",
        "ledger": "global"
    }}
    :args:
        name:str - cluster name
        company:str - company that owns the cluster
        parent_cluster:str - parent cluster ID
        db_name:str - specific database for a given cluster
        table_name:str - specific table in a given cluster
        exception:bool - whether to print exceptions
    :params:
        policy:dict - generated cluster policy
    :return:
        policy as a JSON string
    """
    policy = {
        "cluster": {
            "name": name,
            "company": company
        }
    }

    if parent_cluster is not None:
        policy["cluster"]["parent"] = parent_cluster
    if db_name is not None:
        if table_name is not None:
            policy["cluster"]["table"] = [{
                "dbms": db_name,
                "name": table_name
            }]
        else:
            policy["cluster"]["dbms"] = db_name

    return support.json_dumps(content=policy, indent=4, exception=exception)


def table_policy(name:str, db_name:str, create_stmt:str, exception:bool=False):
    """
    Create table policy
    :sample table:
    {"table": {
        "name": "rand_data",
         "dbms": "test",
         "create": "CREATE TABLE IF NOT EXISTS rand_data(  "
                                "row_id SERIAL PRIMARY KEY,"
                                "insert_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),"
                                "tsd_name CHAR(3),"
                                "tsd_id INT,"
                                "timestamp timestamp not null default now(),"
                                "value int"
                        ");"
                        "CREATE INDEX rand_data_timestamp_index ON rand_data(timestamp);"
                        "CREATE INDEX rand_data_tsd_index ON rand_data(tsd_name, tsd_id);"
                        "CREATE INDEX rand_data_insert_timestamp_index ON rand_data(insert_timestamp);",
             "source": "Processing JSON file",
             "id": "c80630a8739acd02220bb1604b2dd93e",
             "date": "2022-12-13T20:38:41.701078Z",
             "ledger": "global"
    }}
    :args:
        name:str - table name
        db_name:str - logical database name
        create_stmt:str - create table statement
        exception:bool - whether to print exceptions
    :params:
        policy:dict - generated policy
    :return:
        policy as JSON string
    """
    policy = {
        'table': {
            'name': name,
            'dbms': db_name,
            'create': create_stmt
        }
    }

    return support.json_dumps(content=policy, indent=4, exception=exception)


def anmp_policy(policy_id:str, content:dict, exception:bool=False):
    """
    The ANMP policy is used for updating information for a given policy. Examples include:
      - updating an IP
      - updating a Port
      - changing policy name
      - changing policy owner (company name)
      - adding new information
    :sample policy:
        {"anmp" : {
            "7a00b26006a6ab7b8af4c400a5c47f2a" : {
                "ip" : !operator_ip,
                "company" : "anylog"
            }
        }
    :args:
        policy_id:str - ID of policy to update
        content:dict - content to include in ANMP policy (ex. {"ip": "127.0.0.1"})
        exception:bool - whether to print exceptions
    :params:
        policy:dict - generated policy
    :return:
        policy as a JSON string
    """
    policy = {
        'anmp': {
            policy_id: content
        }
    }

    return support.json_dumps(content=policy, indent=4, exception=exception)


def generic_policy(policy_type:str, content:dict, exception:bool=False):
    """
    Generic policy creator
    :args:
        policy_type:str - policy type
        content:dict - content to include in policy (ex. {"hello": "world"})
        exception:bool - whether to print exceptions
        :params:
        policy:dict - generated policy
    :return:
        policy as a JSON string
    """
    policy = {policy_type: content}

    return support.json_dumps(content=policy, indent=4, exception=exception)

