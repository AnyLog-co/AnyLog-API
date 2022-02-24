import os
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).split('anylog_scripts')[0]
REST_PATH = os.path.join(ROOT_PATH, 'REST')
sys.path.insert(0, REST_PATH)

from anylog_connection import AnyLogConnection
import blockchain_calls
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
    anylog_conn = AnyLogConnection(conn=conn, auth=auth, timeout=timeout)

    # validate status
    if not generic_get_calls.validate_status(anylog_conn=anylog_conn, exception=exception):
        print(f'Failed to validate connection to AnyLog on {anylog_conn.conn}')
        exit(1)

    anylog_dictionary = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, exception=exception)

    # create ledger
    while 'blockchain' not in database_calls.get_dbms(anylog_conn=anylog_conn, exception=exception):
        database_calls.connect_dbms(anylog_conn=anylog_conn, db_name='blockchain', db_type=anylog_dictionary['db_type'],
                                    db_ip=anylog_dictionary['db_port'], db_port=anylog_dictionary['db_port'],
                                    db_user=anylog_dictionary['db_user'],
                                    db_passwd=anylog_dictionary['default_dbms'], exception=exception)
        if db_name not in database_calls.get_dbms(anylog_conn=anylog_conn, exception=exception):
            anylog_dictionary['db_type'] = 'sqlite'

    if 'blockchain' in database_calls.get_dbms(anylog_conn=anylog_conn, exception=exception):
        database_calls.create_table(anylog_conn=anylog_conn, db_name='blockchain', table_name='ledger',
                                    exception=exception)

    # declare policies
    if 'loc' not in anylog_dictionary:
        location = generic_get_calls.get_location(exception=exception)
    else:
        location = anylog_dictionary['loc']

    # Master
    if 'company_name' in anylog_dictionary:
        print('test')
    exit(1)
    print(anylog_dictionary['company_name'])
    if blockchain_calls.blockchain_get(anylog_conn=anylog_conn, policy_type='master',
                                       where_condition=f"name={anylog_dictionary['node_name']} and company={anylog_dictionary['company_name']} and ip={anylog_dictionary['external_ip']} and port={anylog_dictionary['anylog_server_port']}",
                                       bring_condition=None, separator=None, exception=exception) is None:
        policy_type = 'master'
        policy_values = {
            "hostname": anylog_dictionary['hostname'],
            "name": anylog_dictionary['node_name'],
            "ip" : anylog_dictionary['external_ip'],
            "local_ip": anylog_dictionary['ip'],
            "company": anylog_dictionary['company_name'],
            "port" : int(anylog_dictionary['anylog_server_port']),
            "rest_port": int(anylog_dictionary['anylog_rest_port']),
            'loc': location
        }

        blockchain_calls.blockcahin_calls.declare_policy(anylog_conn=anylog_conn, policy_type=policy_type,
                                                         company_name=anylog_dictionary['company_name'],
                                                         policy_values=policy_values,
                                                         master_node=anylog_dictionary['master_node'],
                                                         exception=False)

    # Cluster
    cluster_id = None
    if blockchain_calls.blockchain_get(anylog_conn=anylog_conn, policy_type='cluster',
                                       where_condition=f"name={anylog_dictionary['cluster_name']} and company={anylog_dictionary['company_name']}",
                                       bring_condition=None, separator=None, exception=exception) is None:
        policy_type = 'cluster'
        policy_values = {
            "company": anylog_dictionary['company_name'],
            "dbms": anylog_dictionary['default_dbms'],
            "name": anylog_dictionary['cluster_name'],
            "master": anylog_dictionary['master_node']
        }
        blockchain_calls.blockcahin_calls.declare_policy(anylog_conn=anylog_conn, policy_type=policy_type,
                                                         company_name=anylog_dictionary['company_name'],
                                                         policy_values=policy_values, master_node=anylog_dictionary['master_node'],
                                                         exception=False)

    cluster_id = blockchain_calls.blockchain_get(anylog_conn=anylog_conn, policy_type='cluster',
                                                 where_condition=f"name={anylog_dictionary['cluster_name']} and company={anylog_dictionary['company_name']}",
                                                 bring_param="first", bring_condition="[cluster][id]", separator=None,
                                                 exception=exception)

    # operator
    if blockchain_calls.blockchain_get(anylog_conn=anylog_conn, policy_type='operator',
                                       where_condition="name=!node_name and company=!company_name and ip=!external_ip and port=!anylog_server_port",
                                       bring_condition=None, separator=None, exception=exception) is None:
        policy_type = 'operator'
        policy_values = {
            "hostname": anylog_dictionary['hostname'],
            "name": anylog_dictionary['node_name'],
            "ip": anylog_dictionary['external_ip'],
            "local_ip": anylog_dictionary['ip'],
            "company": anylog_dictionary['company_name'],
            "port": int(anylog_dictionary['anylog_server_port']),
            "rest_port": int(anylog_dictionary['anylog_rest_port']),
            'loc': location
        }
        if cluster_id is not None:
            policy_values['cluster'] = cluster_id

        blockchain_calls.blockcahin_calls.declare_policy(anylog_conn=anylog_conn, policy_type=policy_type,
                                                         company_name=company_name, policy_values=policy_values,
                                                         master_node=master_node, exception=False)

if __name__ == '__main__':
    main(conn='10.0.0.111:2149', auth=(), timeout=30, exception=True)