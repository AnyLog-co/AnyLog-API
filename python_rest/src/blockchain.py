import anylog_connector
import find_location
from generic_post import post_cmd
from generic_get import get_cmd


def create_node_policy(anylog_conn:anylog_connector.AnyLogConnector, policy_type:str, configuration:dict,
                       cluster_id:str=None, scripts:list=[], exception:bool=False):
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

    if isinstance(scripts, list) and scripts != []:
        new_policy[policy_type]["scripts"] = scripts
    elif isinstance(scripts, str):
        new_policy[policy_type]["scripts"] = [scripts]

    return new_policy


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
    command= f"run blockchain sync where source={source} and time={time} and dest={dest} and connection={connection}",

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
    command = f"blockchain get (",
    for policy in policy_type.split(','):
        command += policy
        if policy != policy_type.split(','):
            command += ","
        else:
            command += ")"

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
    command = "blockchain prepare policy !new_policy",
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
