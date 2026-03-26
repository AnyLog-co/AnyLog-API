import ast

def create_policy(policy_type:str, **kwargs)->dict:
    policy_type = policy_type.strip().replace(' ', '_')
    new_policy = {
        policy_type: {}
    }

    for name, value in kwargs:
        if value:
            try:
                new_policy[policy_type][name] = ast.literal_eval(value)
            except:
                new_policy[policy_type][name] = value

    return new_policy


def config_policy(policy_name:str=None, policy_id:str=None, scripts:list=[], **kwargs)->dict:
    """
    Method for generating a configuration policy

    to configure the policy to do network connectivity  we recommend using AnyLog's env vars
    as opposed to hard-coding it.

    Example:
        config_policy(policy_id="operator-configs",  ip="'!ip'", port="'!anylog_server_port'" ...)
    :args:
        policy_name:str - policy name
        policy_id:str - policy ID
        scripts:list - list of scripts to execute
        kwargs:dict user defined configs
    """


def node_policy(node_type:str, node_name:str,  external_ip:str, server_port:int, rest_port:int, local_ip:str=None,
                broker_port:int=None, hostname:str=None, main:bool=False, cluster_id:str=None, **kwargs)->dict:
    """
    Method to generate a node policy
    :args:
        node_type:str - node type (master, operator, query, publisher)
        node_name:str - node name
        external_ip:str - (external) IP address for node
        server_port:int - TCP connection port
        restr_port:int - REST connection port
        local_ip:str - (local) IP address for the node
        broker_port:int - Message Broker connection port
        hostname:str - node's hostname
        main:bool - for  Operator node(s)  whether it's a primary or secondary node in the cluster (there can only be 1 primary per cluster)
        cluster_id:str - for Operator node(s)  the cluster (ID) they're associated with
        kwargs:dict - user defined params they feel necessarily for policy
    :return:
        generated policy
    """

    if node_type.lower() == "operator" and not cluster_id:
        raise ValueError(f"A node of type {node_type.capitalize()} must have a cluster ID")

    return create_policy(policy_type=node_type, node_name=node_name, external_ip=external_ip, server_port=server_port,
                         rest_port=rest_port, local_ip=local_ip, broker_port=broker_port, hostname=hostname,
                         main=main, cluster_id=cluster_id, **kwargs)


def cluster_policy()->dict:
    pass
