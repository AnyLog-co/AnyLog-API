from anylog_api_py.support import dict_to_string


def create_config_policy(policy_name:str, company_name:str, external_ip:str, local_ip:str, anylog_server_port,
                         anylog_rest_port, anylog_broker_port=None, tcp_bind:bool=False, rest_bind:bool=False,
                         broker_bind:bool=False):
    """
    Create configuration policy
    :sample policy:
        {"config": {
            "name": "node-network-config",
            "company": "New Company",
            "ip": "!external_ip",
            "local_ip": "!ip",
            "port": "'!anylog_server_port.int'",
            "rest_port":
            "'!anylog_rest_port.int'"
        }}
    :args:
       policy_name:str - configuration policy name
       company_name:str - company associated with this policy
       external_ip:str - external IP address
       local_ip:str - local IP address
       anylog_server_port - TCP port
       anylog_rest_port - REST port
       anylog_broker_port - broker port
       tcp_bind:bool - bind on TCP against local_ip
       rest_bind:bool - bind on REST against local_ip
       broker_bind:bool - bind on broker against local_ip
    :params:
        config_policy:dict - generated configuration policy
    :return:
        config_policy as string
    """
    config_policy = {"config": {
        "name": policy_name,
        "company": company_name
    }}

    config_policy["config"]["ip"] = local_ip
    if tcp_bind is False:
        config_policy["config"]["ip"] = external_ip
        config_policy["config"]["local_ip"] = local_ip

    config_policy["config"]["port"] = anylog_rest_port
    if isinstance(anylog_server_port, str):
        config_policy["config"]["port"] = f"'{anylog_server_port}.int'"

    if rest_bind is True:
        config_policy["config"]["rest_ip"] = local_ip

    config_policy["config"]["rest_port"] = anylog_rest_port
    if isinstance(anylog_rest_port, str):
        config_policy["config"]["rest_port"] = f"'{anylog_rest_port}.int'"

    if anylog_broker_port is not None:
        if broker_bind is True:
            config_policy["config"]["broker_ip"] = local_ip

        config_policy["config"]["broker_port"] = anylog_broker_port
        if isinstance(anylog_broker_port, str):
            config_policy["config"]["broker_port"] = f"{anylog_broker_port}.int"

    return dict_to_string(config_policy)

