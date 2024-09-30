import anylog_api.anylog_connector as anylog_connector
import anylog_api.blockchain.cmds as blockchain_cmds

def master(conn:anylog_connector.AnyLogConnector, params:dict, destination:str="", view_help:bool=False,
           return_cmd:bool=False, exception:bool=False):
    """
    Deploy Master node
    :steps:
        1. connect database
        2. node policy
        3. scheduler 1
    """
    where_conditions = f"name={params['node_name']} and company=\"{params['company_name']}\""
    if params['tcp_bind'] is False:
        where_conditions += f" and ip={params['external_ip']}"
    elif params['tcp_bind'] is True and 'overlay_ip' in params:
        where_conditions += f" and ip={params['overlay_ip']}"
    elif params['tcp_bind'] is True:
        where_conditions += f" and ip={params['ip']}"

    if params['tcp_bind'] is False and 'overlay_ip' in params:
        where_conditions += f" and ip={params['overlay_ip']}"
    elif params['tcp_bind'] is False:
        where_conditions += f" and ip={params['local_ip']}"
    where_conditions += f" and port={params['anylog_server_port']}"

    is_policy = blockchain_cmds.get_policy(conn=conn, policy_type=params['node_type'], where_condition=where_conditions,
                                           bring_case="first", bring_condition="[*][id]", seperator=",",
                                           destination=destination, view_help=view_help, return_cmd=return_cmd,
                                           exception=exception)




