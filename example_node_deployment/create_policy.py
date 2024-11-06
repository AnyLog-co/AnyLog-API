import anylog_api.anylog_connector as anylog_connector
import anylog_api.blockchain.cmds as blockchain_cmds
import anylog_api.blockchain.policies as blockchain_policies
from anylog_api.generic.get_location import get_location
import example_node_deployment.__support__ as support


def create_cluster(conn:anylog_connector.AnyLogConnector, cluster_name:str, owner:str, ledger_conn:str, db_name:str=None,
                   table:str=None, parent:str=None, destination:str=None, view_help:bool=False, return_cmd:bool=False,
                   exception:bool=False):
    """
    Create cluster policy on the network
    :args:
        conn:anylog_connector.AnyLogConnector - Connection to AnyLog
        cluster_name:str - cluster name
        owner:str - cluster owner
        ledger_conn:str - ledger connection information
        destination:str - remote connection information
        view_help:bool - print help information
        return_cmd:bool - return command to be executed
        exception:bool - print exception
    :optional-args:
        db_name:str - logical database name
        table:str - table name associated name
        parent:str - parent cluster ID
    :params:
        cluster_id:str - cluster ID
        counter:int - number of times the insert was attempted
        where_condition:str - `blockchain get` WHERE
        cluster_policy:dict - generated policy
    :return:
        cluster_id
    """
    cluster_id = None
    counter = 0
    where_condition = f"name={cluster_name} and company={owner}"
    cluster_policy = blockchain_policies.create_cluster_policy(name=cluster_name, owner=owner, db_name=db_name,
                                                               table=table, parent=parent)


    while cluster_id is None:
        cluster_id = blockchain_cmds.get_policy(conn=conn, policy_type='cluster', where_condition=where_condition,
                                               bring_case="first", bring_condition="[*][id]", destination=destination,
                                               view_help=view_help, return_cmd=return_cmd, exception=exception)
        if parent is None and (db_name or table) and cluster_id:
            cluster_policy = blockchain_policies.create_cluster_policy(name=cluster_name, owner=owner, db_name=db_name,
                                                                       table=table, parent=cluster_id)
        if counter == 0 and cluster_id is None:
            if blockchain_cmds.prepare_policy(conn=conn, policy=cluster_policy, destination=destination,
                                              view_help=view_help, return_cmd=return_cmd, exception=exception) is not True:

                print(f'Issue with blockchain policy, cannot declare policy on blockchain...')
            else:
                blockchain_cmds.post_policy(conn=conn, policy=cluster_policy, ledger_conn=ledger_conn,
                                            destination=destination, view_help=view_help,return_cmd=return_cmd,
                                            exception=exception)
            counter += 1
        if not cluster_id:
            print(f"Failed to declare cluster policy against {ledger_conn}, cannot continue...")
            exit(1)

    return cluster_id


def generate_policy(conn:anylog_connector.AnyLogConnector, params:dict, cluster_id:str=None, destination:str=None,
                    view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Deploy Master node
    :steps:
        1. connect database
        2. node policy
        3. scheduler 1
    """
    policy_id = None
    # validate params
    support.validate_configs(params=params)
    i = 0
    ip, local_ip = support.extract_ips(params=params)

    # check policy exists
    where_conditions = f"name={params['node_name']} and ip={ip} and port={params['anylog_server_port']}"
    is_policy = blockchain_cmds.get_policy(conn=conn, policy_type=params['node_type'], where_condition=where_conditions,
                                           bring_case="first", destination=destination, view_help=view_help,
                                           return_cmd=return_cmd, exception=exception)

    if not is_policy:
        location = get_location(conn=conn, params=params, destination=destination, view_help=view_help,
                                return_cmd=return_cmd, exception=exception)
        if 'anylog_broker' in params:
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
        else:
            # blockchain sync
            status, cmd = blockchain_cmds.blockchain_sync(conn=conn, ledger_conn=params['ledger_conn'],
                                                          blockchain_source=params['blockchain_source'], )

        is_policy = blockchain_cmds.get_policy(conn=conn, policy_type=params['node_type'],
                                               where_condition=where_conditions,
                                               bring_case="first", destination=destination, view_help=view_help,
                                               return_cmd=return_cmd, exception=exception)

    if is_policy and params['node_type'] in is_policy[0] and 'id' in is_policy[0][params['node_type']]:
        policy_id = is_policy[0][params['node_type']]['id']
    return policy_id



