import os
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).split('anylog_scripts')[0]
REST_PATH = os.path.join(ROOT_PATH, 'REST')
sys.path.insert(0, REST_PATH)

from anylog_connection import AnyLogConnection
import blockcahin_calls
import database_calls
import deployment_calls
import generic_get_calls
import generic_post_calls


def main(conn:str, auth:tuple=(), timeout:int=30, exception:bool=False):
    """
    The following is intended to support deploying "static" parameters in AnyLog
        - create work dirs
        - create tables
        - declare policies
    :args:
        conn:str - REST IP:PORT for communicating with AnyLog
        auth:tuple - authentication information
        timeout:int - REST timeout (in seconds)
        exception:bool - whether to print exception
    :params:
        db_table_list:dict - dictionary of database with their corresponding tables that should be created
        anylog_conn:AnyLogConnection - connection to AnyLog via REST
        node_status:bool - whether or not able to `get status` of node
        db_list:list - list of connected databases
        # policy specific params
        company_name:str - company name
        location:str - device location
        master_node:str - Master node credentials (TCP - IP:PORT)
        policy_type:str - policy type to create
        policy_values:dict - dictionary of values correlated to policy
    """
    db_table_list = {'blockchain': 'ledger', 'almgm': 'tsd_info'}
    anylog_conn = AnyLogConnection(conn=conn, auth=auth, timeout=timeout)

    # validate status
    node_status = generic_get_calls.get_status(anylog_conn=anylog_conn, exception=exception)
    if not node_status:
        print(f'Failed to validate connection to AnyLog on {anylog_conn.conn}')
        exit(1)

    # create tables
    db_list = database_calls.get_dbms(anylog_conn=anylog_conn, exception=exception)
    for db_name in db_table_list:
        database_calls.create_table(anylog_conn=anylog_conn, db_name=db_name, table_name=db_table_list[db_name],
                                    exception=exception)

    # declare policies
    cluster_id = None
    company_name = 'Ai-Ops'
    location = generic_get_calls.get_location(exception=exception)
    master_node = "!master_node"

    # Master
    if blockchain_get(anylog_conn=anylog_conn, policy_type='master', where_condition="name=!node_name and company=!company_name and ip=!external_ip and port=!anylog_server_port",
                      bring_condition=None, separator=None, exception=exception) is None:
        policy_type = 'master'
        policy_values = {
            "hostname": "!hostname",
            "name": "!node_name",
            "ip" : "!external_ip",
            "local_ip": "!ip",
            "company": "!company_name",
            "port" : "!anylog_server_port.int",
            "rest_port": "!anylog_rest_port.int",
        }
        if "loc" not in policy_values and policy_type != 'cluster':
            policy_values['loc'] = location
        blockcahin_calls.declare_policy(anylog_conn=anylog_conn, policy_type=policy_type, company_name=company_name,
                                        policy_values=policy_values, master_node=master_node, exception=False)

    # Cluster
    if blockchain_get(anylog_conn=anylog_conn, policy_type='cluster', where_condition="name=!cluster_name and company=!company_name",
                      bring_condition=None, separator=None, exception=exception) is None:
        policy_type = 'cluster'
        policy_values = {
            "company": "!company_name",
            "dbms": "!default_dbms",
            "name": "!cluster_name",
            "master": "!master_node"
        }
        blockcahin_calls.declare_policy(anylog_conn=anylog_conn, policy_type=policy_type, company_name=company_name,
                                        policy_values=policy_values, master_node=master_node, exception=False)

    cluster_id = blockchain_get(anylog_conn=anylog_conn, policy_type='cluster', where_condition="name=!cluster_name and company=!company_name",
                                bring_param="first", bring_condition="[cluster][id]", separator=None,
                                exception=exception)

    # operator
    if blockchain_get(anylog_conn=anylog_conn, policy_type='operator', where_condition="name=!node_name and company=!company_name and ip=!external_ip and port=!anylog_server_port",
                      bring_condition=None, separator=None, exception=exception) is None:
        policy_type = 'operator'
        policy_values = {
            "hostname": "!hostname",
            "name": "!node_name",
            "ip" : "!external_ip",
            "local_ip": "!ip",
            "company": "!company_name",
            "port" : "!anylog_server_port.int",
            "rest_port": "!anylog_rest_port.int",
        }
        if "loc" not in policy_values and policy_type != 'cluster':
            policy_values['loc'] = location
        if cluster_id is not None:
            policy_values['cluster'] = cluster_id
        blockcahin_calls.declare_policy(anylog_conn=anylog_conn, policy_type=policy_type, company_name=company_name,
                                        policy_values=policy_values, master_node=master_node, exception=False)
