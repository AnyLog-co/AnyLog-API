import os
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).split('anylog_scripts')[0]
REST_PATH = os.path.join(ROOT_PATH, 'REST')
sys.path.insert(0, REST_PATH)

from anylog_connection import AnyLogConnection
import authentication
import database_calls
import deployment_calls
import generic_get_calls
import generic_post_calls


def main(conn:str, auth:tuple=(), timeout:int=30, exception:bool=False):
    """
    The following is intended as an example of deploying Master Node with blockchain policy declaration(s).
    :args:
        conn:str - REST IP:PORT for communicating with AnyLog
        auth:tuple - authentication information
        timeout:int - REST timeout (in seconds)
        exception:bool - whether to print exception
    :params:
        anylog_conn:AnyLogConnection - connection to AnyLog via REST
        anylog_dictionary:dict - dictionary of AnyLog params
        drop_partition_task:str - command for dropping partition
        # database creation specific params
        db_status:bool - whether or not database exists
        db_type:str - database type
    """
    anylog_conn = AnyLogConnection(conn=conn, auth=auth, timeout=timeout)

    # validate status
    print("Validate Connection")
    if not generic_get_calls.validate_status(anylog_conn=anylog_conn, exception=exception):
        print(f'Failed to validate connection to AnyLog on {anylog_conn.conn}')
        exit(1)

    anylog_dictionary = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, exception=exception)
    authentication.disable_authentication(anylog_conn=anylog_conn, exception=exception)

    # set home path & create work dirs
    print("Set Directories")
    generic_post_calls.set_home_path(anylog_conn=anylog_conn, anylog_root_dir=anylog_dictionary['anylog_root_dir'],
                                     exception=exception)
    generic_post_calls.create_work_dirs(anylog_conn=anylog_conn, exception=exception)

    # Set AnyLog params & extract them
    print("Set Params & Extract Dictionary")
    hostname = generic_get_calls.get_hostname(anylog_conn=anylog_conn, exception=exception)
    if hostname != '':
        generic_post_calls.set_variables(anylog_conn=anylog_conn, key='hostname', value=hostname, exception=exception)

    node_id = authentication.get_node_id(anylog_conn=anylog_conn, exception=exception)
    if not isinstance(node_id, str):
        while int(node_id.status_code) != 200:
            authentication.create_public_key(anylog_conn=anylog_conn, password='passwd', exception=exception)
            node_id = authentication.get_node_id(anylog_conn=anylog_conn, exception=exception)
    generic_post_calls.set_variables(anylog_conn=anylog_conn, key='node_id', value=node_id, exception=exception)

    anylog_dictionary = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, exception=exception)

    get_process = generic_get_calls.get_processes(anylog_conn=anylog_conn, exception=exception)
    """
    connect to logical database(s) - if fails to connect reattempt using SQLite.
    """
    print("Connect to Databases")
    for db_name in ['system_query']:
        while db_name not in database_calls.get_dbms(anylog_conn=anylog_conn, exception=exception):
            database_calls.connect_dbms(anylog_conn=anylog_conn, db_name=db_name, db_type=anylog_dictionary['db_type'],
                                        db_ip=anylog_dictionary['db_port'], db_port=anylog_dictionary['db_port'],
                                        db_user=anylog_dictionary['db_user'],
                                        db_passwd=anylog_dictionary['default_dbms'], exception=exception)
            if db_name not in database_calls.get_dbms(anylog_conn=anylog_conn, exception=exception):
                anylog_dictionary['db_type'] = 'sqlite'


    # Set schedulers
    print("Set Scheduler(s)")
    if get_process['Scheduler'] == 'Not declared':
        generic_post_calls.run_scheduler1(anylog_conn=anylog_conn, exception=exception)

    if get_process['Blockchain Sync'] == 'Not declared':
        generic_post_calls.blockchain_sync_scheduler(anylog_conn=anylog_conn, source="master",
                                                     time=anylog_dictionary['sync_time'], dest="file",
                                                     connection=anylog_dictionary['master_node'], exception=exception)

    # declare policies
    if 'loc' not in anylog_dictionary:
        location = generic_get_calls.get_location(exception=exception)
    else:
        location = anylog_dictionary['loc']

    # Query
    print('Declare Query')
    if not blockchain_calls.blockchain_get(anylog_conn=anylog_conn, policy_type='query',
                                           where_condition=f"name={anylog_dictionary['node_name']} and company={anylog_dictionary['company_name']} and ip={anylog_dictionary['external_ip']} and port={anylog_dictionary['anylog_server_port']}",
                                           bring_condition=None, separator=None, exception=exception):
        policy_type = 'query'
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

        policy = support.build_policy(policy_type=policy_type, company_name=anylog_dictionary['company_name'],
                                      policy_values=policy_values)
        blockchain_calls.declare_policy(anylog_conn=anylog_conn, policy=policy,
                                        master_node=anylog_dictionary['master_node'], exception=False)


if __name__ == '__main__':
    main(conn='10.0.0.111:2149', auth=(), timeout=30, exception=True)