import anylog_connector
import find_location


def create_node_policy(anylog_conn:anylog_connector.AnyLogConnector, policy_type:str, configuration:dict,
                       cluster_id:str=None, exception:bool=False):
    """
    Create a node policy
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - AnyLog REST connection
        policy_type:str - Node policy type (master, operator, query, publisher)
        configuration:dict - configurations
        cluster_id:str - Cluster ID for operator
        exception:bool - whether to print exceptions
    :params:
        new_policy:dict - generated policy
        location:str, country:str, state:str, city:str - location of machine
    :return
        new_policy
    """
    new_policy = {policy_type: {}}
    if "node_name" in configuration:
        new_policy[policy_type]["name"] = configuration["node_name"]
    if "company_name" in configuration:
        new_policy[policy_type]["company"] = configuration["company_name"]
    if "hostname" in configuration:
        new_policy[policy_type]["hostname"] = configuration["hostname"]

    if "tcp_bind" in configuration and configuration["tcp_bind"] is False:
        new_policy[policy_type]["ip"] = configuration["external_ip"]
        new_policy[policy_type]["local_ip"] = configuration["ip"]
    elif "tcp_bind" in configuration and configuration["tcp_bind"] is False:
        new_policy[policy_type]["external_ip"] = configuration["external_ip"]
        new_policy[policy_type]["ip"] = configuration["ip"]

    if "proxy_ip" in configuration:
        new_policy[policy_type]["proxy_ip"] = configuration["proxy_ip"]

    if "anylog_server_port" in configuration:
        new_policy[policy_type]["port"] = configuration["anylog_server_port"]
    if "anylog_rest_port" in configuration:
        new_policy[policy_type]["rest_port"] = configuration["anylog_rest_port"]
    if "anylog_server_port" in configuration:
        new_policy[policy_type]["port"] = configuration["anylog_server_port"]
    if "anylog_broker_port" in configuration:
        new_policy[policy_type]["broker_port"] = configuration["anylog_broker_port"]
    if policy_type == "operator" and cluster_id is not None:
        new_policy[policy_type]["cluster"] = cluster_id

    location, country, state, city = find_location.get_location(anylog_conn=anylog_conn, exception=exception)
    print(location, country, state, city)
    if "location" in configuration and configuration["location"] != "Unknown":
        new_policy[policy_type]["loc"] = configuration["location"]
    elif location is not None and location != "location":
        new_policy[policy_type]["loc"] = location
    if "country" in configuration and configuration["country"] != "Unknown":
        new_policy[policy_type]["country"] = configuration["country"]
    elif country is not None and country != "country":
        new_policy[policy_type]["country"] = country
    if "state" in configuration and configuration["state"] != "Unknown":
        new_policy[policy_type]["state"] = configuration["state"]
    elif state is not None and state != "state":
        new_policy[policy_type]["state"] = state
    if "city" in configuration and configuration["city"] != "Unknown":
        new_policy[policy_type]["city"] = configuration["city"]
    elif city is not None and city != "city":
        new_policy[policy_type]["city"] = city

    return new_policy


def run_synchronizer(anylog_conn:anylog_connector.AnyLogConnector, source:str, time:str, dest:str, connection:str,
                     view_help:bool=False):
    """
    Initiate the blockchain sync process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#blockchain-synchronizer
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog via REST
        source:str - the source of the metadata (blockchain or a Master Node)
        dest:str - The destination of the blockchain data such as a file (a local file) or a DBMS (a local DBMS).
        The connection information that is needed to retrieve the data. For a Master, the IP and Port of the master/ledger node
        time:str - the frequency of updates.
        view_help:bool - view help regarding command
    :params
        status:bool
        headers:dict - REST header information
        r:requests.model.Response - response from REST request
    :return:
        status
    """
    status = False
    headers = {
        "command": f"run blockchain sync where source={source} and time={time} and dest={dest} and connection={connection}",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(anylog_conn=anylog_conn, cmd=headers['command'])
        return None

    r = anylog_conn.post(headers=headers)
    if r is None or int(r.status_code) != 200:
        status = False

    return status


def get_policy(anylog_conn:anylog_connector.AnyLogConnector, policy_type:str="*", where_conditions:dict=None,
               bring_conditions:str=None, bring_values:str=None, separator:str=None, view_help:bool=False):
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
        view_help:bool - get informmation regarding command
    :params:
        headers:dict - REST header
        output:list - results
    :return:
        if help returns None
        else execute GET and return results
    """
    headers = {
        "command": f"blockchain get ({policy_type})",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(anylog_conn=anylog_conn, cmd=headers['command'])
        return None

    if len(where_conditions) > 0:
        headers["command"] += " where "
        for param in where_conditions:
            if isinstance(where_conditions[param], int) or isinstance(where_conditions[param], float):
                headers["command"] += f"{param}={where_conditions[param]} "
            else:
                headers["command"] += f'{param}="{where_conditions[param]}" '
            if param != list(where_conditions.keys())[-1]:
                headers["command"] += "and "
    if bring_conditions is not None or bring_values is not None:
        if bring_conditions is not None:
            headers["command"] += f" bring.{bring_conditions} "
        else:
            headers["command"] += f" bring "
        if bring_values is not None:
            headers["command"] += f" {bring_values}"
        if separator is not None:
            headers["command"] += f" separator={separator}"

    return anylog_conn.get(headers=headers)


