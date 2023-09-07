import blockchain

from anylog_api_py.networking import create_config_policy
from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.blockchain import get


def get_config_policy_id(anylog_connector:AnyLogConnector, company_name:str, policy_name:str, exception:bool=False)->str:
    """
    Get policy ID or config
    :args:
        anylog_connector:AnyLogConnector - connection to AnyLog node
        company_name;str - company to search by
        policy_name:str - policy name
        exception:bool - whether to print exceptions or not
    :params:
        policy_id:str - policy ID(s) from blockchain
    """
    policy_id = get(anylog_conn=anylog_connector, policy_types=['config'],
                    where_conditions=[f"company='{company_name}]'", f"name={policy_name}"],
                    bring_conditions="[config][id]", separator="' '", exception=exception)

    return policy_id


def network_main(anylog_connector:AnyLogConnector, configs:dict, exception:bool=False):
    """
    Declare network configuration on the node
    :args:

    """
    anylog_broker_port = None
    tcp_bind = False
    rest_bind = False
    broker_bind = False
    if "tcp_bind" in configs and configs["tcp_bind"] in ["true", "True", "TRUE", True]:
        tcp_bind = True
    if "rest_bind" in configs and configs["rest_bind"] in ["true", "True", "TRUE", True]:
        rest_bind = True

    if "anylog_broker_port" in configs:
        anylog_broker_port = configs["anylog_broker_port"]
        if "broker_bind" in configs and configs["broker_bind"] in ["true", "True", "TRUE", True]:
            broker_bind = True

    if "policy_based_networking" in configs and configs["policy_based_networking"] in ["true", "True", "TRUE", True]:
        policy_name = "new-config-policy"

        if "config_policy_name" in configs:
            policy_name = configs["config_policy_name"]

        new_policy = create_config_policy(policy_name=policy_name, company_name=configs["company_name"],
                                          external_ip="!external_ip", local_ip="!ip",
                                          anylog_server_port="!anylog_server_port",
                                          anylog_rest_port="!anylog_rest_port",
                                          anylog_broker_port=anylog_broker_port,
                                          tcp_bind=tcp_bind, rest_bind=rest_bind,
                                          broker_bind=broker_bind)
        blockchain.

