import anylog_connector
from generic_post import post_cmd
from generic_get import get_cmd


def create_cluster_policy(name:str, company_name:str, db_name:str=None, table_name:str=None, parent:str=None):
    """
    Create cluster policy
    :args:
        name:str - cluster name
        company_name:str - company cluster is associated with
        db_name:str - logical database name
        table_name:str - logical table for a given cluster
        parent:str - cluster parent ID
    :params;
        new_policy:dict  - generated policy
    :return:
        new_policy
    """
    new_policy = {
        "cluster": {
            "name": name,
            "company": company_name
        }
    }

    if parent is not None:
        new_policy["cluster"]["parent"] = parent

    if db_name is not None and table_name is not None:
        new_policy["cluster"]["table"] = {
            "dbms": db_name,
            "table": table_name
        }
    elif db_name is not None:
        new_policy["cluster"]["dbms"] = db_name

    return new_policy


def create_node_policy(policy_type:str, node_name:str, company_name:str, ip:str, server_port:int, hostname:str=None,
                       external_ip:str=None, rest_port:int=None, broker_port:int=None, proxy_ip:str=None,
                       cluster_id:str=None, location:str=None, country:str=None, state:str=None, city:str=None):
    """
    Create a node policy
    :args:
        policy_type:str - Node policy type (master, operator, query, publisher)
        node_name:str - node name
        company_name:str - company
        ip:str - IP address
        server_port:int - AnyLog TCP port connection
        hostname:str - hostname
        external_ip:str - external IP
        rest_port:int - AnyLog REST port connection
        broekr_port:int - AnyLog Broker port connection
        proxy_ip:str - proxy IP address
        cluster_id:str - Cluster ID for operator
        location:str - location coordinates
        country:str
        state:str
        city:str
    :params:
        new_policy:dict - generated policy
    :return
        new_policy
    """
    new_policy = {policy_type: {
        "name": node_name,
        "company": company_name
    }}

    if hostname is not None:
        new_policy[policy_type]["hostname"] = hostname

    new_policy[policy_type]["ip"] = ip
    if external_ip is not None:
        new_policy[policy_type]["external_ip"] = external_ip
    if proxy_ip is not None:
        new_policy[policy_type]["proxy_ip"] = proxy_ip

    new_policy[policy_type]["port"] = server_port
    if rest_port is not None:
        new_policy[policy_type]["rest_port"] = rest_port
    if broker_port is not None:
        new_policy[policy_type]["broker_port"] = broker_port

    if cluster_id is not None and policy_type == "operator":
        new_policy[policy_type]["cluster"] = cluster_id

    if location is not None:
        new_policy[policy_type]["loc"] = location
    if country is not None:
        new_policy[policy_type]["country"] = country
    if state is not None:
        new_policy[policy_type]["state"] = state
    if city is not None:
        new_policy[policy_type]["city"] = city

    return new_policy


def create_config_policy(configs:dict={}, scripts:list=[]):
    """
    Generate a configuration policy
    :args:
        policy_name:str - policy name
        network_configs:dict - network configuration
            Note values are taken literally
        scripts:list - list of scripts to execute
    :params:
        config_policy:dict - generated config policy
    """
    config_policy = {
        "config": {
        }
    }

    for config in configs:
        config_policy["config"][config] = configs[config]

    if len(scripts) > 0 and isinstance(scripts, list):
        config_policy["config"]["script"] = scripts

    return config_policy


def run_synchronizer(anylog_conn:anylog_connector.AnyLogConnector, source:str, time:str, dest:str, connection:str,
                     destination:str=None, execute_cmd:bool=True, view_help:bool=False):
    """
    Initiate the blockchain sync process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#blockchain-synchronizer
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog via REST
        source:str - the source of the metadata (blockchain or a Master Node)
        dest:str - The destination of the blockchain data such as a file (a local file) or a DBMS (a local DBMS).
        connection - the connection information that is needed to retrieve the data.
            For a Master, the IP and Port of the master/ledger node
        time:str - the frequency of updates.
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - whether to print help information
    :params:
        status:bool
        headers:dict - REST header information
        r:requests.model.Response - response from REST request
    :return:
        status
    """
    command=f"run blockchain sync where source={source} and time={time} and dest={dest} and connection={connection}"

    return post_cmd(anylog_conn=anylog_conn, command=command, payload=None, destination=destination,
                    execute_cmd=execute_cmd, view_help=view_help)


def get_policy(anylog_conn:anylog_connector.AnyLogConnector, policy_type:str="*", where_conditions:dict=None,
               bring_conditions:str=None, bring_values:str=None, separator:str=None, destination:str=None,
               execute_cmd:bool=True, view_help:bool=False):
    """
    execute `blockchain get` command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/blockchain%20commands.md#query-policies
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - AnyLog REEST connection
        policy_type:str - policy(s) to query for
        where_conditions:dict - where conditions
        bring_conditions:str - bring condition (ex. first, last, unique)
        bring_values:str - values to bring
        seperator:str - how to separate results if using bring command
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - whether to print help information
    :params:
        headers:dict - REST header
        output:list - results
    :return:
        if help returns None
        else execute GET and return results
    """
    command = f"blockchain get {policy_type}"
    if len(policy_type.split(",")) > 1:
        command = f"blockchain get ("
        for policy in policy_type.split(","):
            command += f"{policy}, "
            if policy == policy_type.split(",")[-1]:
                command = command.rsplit(",")[0] + ")"

    if len(where_conditions) > 0:
        command += " where "
        for param in where_conditions:
            if isinstance(where_conditions[param], int) or isinstance(where_conditions[param], float):
                command += f"{param}={where_conditions[param]} "
            else:
                command += f'{param}="{where_conditions[param]}" '
            if param != list(where_conditions.keys())[-1]:
                command += "and "
    if bring_conditions is not None or bring_values is not None:
        if bring_conditions is not None:
            command += f" bring.{bring_conditions} "
        else:
            command += f" bring "
        if bring_values is not None:
            command += f" {bring_values}"
        if separator is not None:
            command += f" separator={separator}"

    return get_cmd(anylog_conn=anylog_conn, command=command, destination=destination, execute_cmd=execute_cmd,
                   view_help=view_help)


def prepare_policy(anylog_conn:anylog_connector.AnyLogConnector, policy:str, destination:str=None,
                   execute_cmd:bool=True, view_help:bool=False):
    """
    Prepare policy
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/blockchain%20commands.md
    :args:
        anylog_conn:anylog_connector.AnyLogConnector
        policy:str - policy to publish
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - whether to print help information
    :params:
        status:bool
        headers:dict - REST headers
    :return:
        status
    """
    command = "blockchain prepare policy !new_policy"
    payload = f"<new_policy={policy}>"

    return post_cmd(anylog_conn=anylog_conn, command=command, payload=payload, destination=destination,
                    execute_cmd=execute_cmd, view_help=view_help)


def publish_policy(anylog_conn:anylog_connector.AnyLogConnector, policy:str=None, local:bool=True, ledger_conn:str=None,
                   blockchain:str=None, destination:str=None, execute_cmd:bool=True, view_help:bool=False):
    """
    Publish policy to blockchain
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/blockchain%20commands.md#the-blockchain-insert-command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - AnyLog connection
        policy:str - policy to publish, if DNE then use pre-existing from prepare_policy
        local:bool - whether to store locally
        ledger_conn:str - master node
        blockchain:str - blockchain
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - whether to print help information
    :params:
        headers:dict - REST headers

    """
    status = True
    command = "blockchain insert where policy=!new_policy"

    if policy is not None:
        payload = f"<new_policy={policy}>"
    if local is True:
        command += f" and local={local}"
    if ledger_conn is not None:
        command += f" and master={ledger_conn}"
    if blockchain is not None:
        command += f" and blockchain={blockchain}"

    return post_cmd(anylog_conn=anylog_conn, command=command, payload=payload, destination=destination,
                    execute_cmd=execute_cmd, view_help=view_help)
