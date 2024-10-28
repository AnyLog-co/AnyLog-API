import anylog_api.anylog_connector as anylog_connector
import anylog_api.blockchain.cmds as blockchain_cmds
import anylog_api.blockchain.policies as blockchain_policies
from anylog_api.generic.get_location import get_location
import example_node_deployment.__support__ as support


def master(conn:anylog_connector.AnyLogConnector, params:dict, destination:str="", view_help:bool=False,
           return_cmd:bool=False, exception:bool=False):
    """
    Deploy Master node
    :steps:
        1. connect database
        2. node policy
        3. scheduler 1
    """
    # validate params
    support.validate_configs(params=params)
    ip, local_ip = support.extract_ips(params=params)

    # check policy exists
    where_conditions = f"name={params['node_name']} and ip={ip} and port={params['anylog_server_port']}"
    is_policy = blockchain_cmds.get_policy(conn=conn, policy_type=params['node_type'], where_condition=where_conditions,
                                           bring_case="first", destination=destination, view_help=view_help,
                                           return_cmd=return_cmd, exception=exception)

    # declare policy
    location = get_location(conn=conn, params=params, destination=destination, view_help=view_help,
                            return_cmd=return_cmd, exception=exception)
    if not is_policy and 'anylog_broker_port' in params:
        policy = blockchain_policies.create_node_policy(node_type=params['node_type'], node_name=params['node_name'],
                                                        owner=params['company_name'], ip=ip, local_ip=local_ip,
                                                        anylog_server_port=params['anylog_server_port'],
                                                        anylog_rest_port=params['anylog_rest_port'],
                                                        anylog_broker_port=params['anylog_broker_port'],
                                                        location=location, cluster_id=None, other_params=None,
                                                        scripts=None)
    else:
        policy = blockchain_policies.create_node_policy(node_type=params['node_type'], node_name=params['node_name'],
                                                        owner=params['company_name'], ip=ip, local_ip=local_ip,
                                                        anylog_server_port=params['anylog_server_port'],
                                                        anylog_rest_port=params['anylog_rest_port'],
                                                        anylog_broker_port=None, location=location,
                                                        cluster_id=None, other_params=None, scripts=None)

    status, cmd = blockchain_cmds.prepare_policy(conn=conn, policy=policy, destination=destination, view_help=view_help,
                                                 return_cmd=return_cmd, exception=exception)
    if status is True:
        status, cmd = blockchain_cmds.post_policy(conn=conn, policy=policy, ledger_conn=params['ledger_conn'],
                                                  destination=destination, view_help=view_help, return_cmd=return_cmd,
                                                  exception=exception)
        if status is False:
            print(f"Failed to declare policy for node type {params['node_type']}")
            exit(1)

    # blockchain sync
    status, cmd = blockchain_cmds.blockchain_sync(conn=conn, ledger_conn=params['ledger_conn'],
                                                  blockchain_source=params['blockchain_source'], )



