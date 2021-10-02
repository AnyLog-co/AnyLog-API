import __init__
import anylog_api
import dbms_cmd
import get_cmd
import post_cmd
import policy_cmd

def format_string(key:str, value:str)->str:
    """
    Format key value pair based on string
    :args:
        key:str - key
        value:str - value to be formatted
    """

def disconnect_node(conn:anylog_api.AnyLogConnect, config:dict, clean_node:bool=False, exception:bool=False):
    """
    Disconnect node from network. If drop_policy is True policy will be dropped
    Steps:
        1. disconnect from processes lin process list
        2. disconnect from databases
        3. If "clean_node" is True:
            - drop database(s)
            - drop policy from node
    :args:
        conn:anylog_api.AnyLogConnect - connect to AnyLog
        config:dict - config from file
        clean_node:bool - to remove everything (but files) from node
        exception:bool - whether to print exceptions
    :params:
        master_node:str - corresponding master node
        process_list:str - AnyLog process list
    """
    if config['node_type'] == 'master':
        master_node = 'local'
    else:
        master_node = config['master_node']

    # disconnect processes
    process_list = get_cmd.get_processes(conn=conn, exception=exception)
    if process_list is not None:
        for process in process_list.split('\n'):
            process_status = True
            if 'running' in process.lower():
                if process.split('|')[0].lstrip().rstrip() == 'Operator':
                    process_status = post_cmd.stop_process(conn=conn, process_name='operator', exception=exception)
                elif process.split('|')[0].lstrip().rstrip() == 'Publisher':
                    process_status = post_cmd.stop_process(conn=conn, process_name='publisher', exception=exception)
                elif process.split('|')[0].lstrip().rstrip() == 'Blockchain Sync':
                    process_status = post_cmd.stop_process(conn=conn, process_name='synchronizer', exception=exception)
                elif process.split('|')[0].lstrip().rstrip() == 'MQTT':
                    process_status = post_cmd.stop_process(conn=conn, process_name='mqtt, exception=exception')
                elif process.split('|')[0].lstrip().rstrip() == 'Scheduler':
                    process_status = post_cmd.stop_process(conn=conn, process_name='scheduler', exception=exception)

                if process_status is False:
                    print('Failed to stop %s' % process.split('|')[0].lstrip().rstrip())

    dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
    for dbms in dbms_list:

    if clean_node is True:
        """
        Drop policy based on the following params: 
            * company name
            * node name
            * external and internal IPs
            * TCP and REST port
        """
        query_parmas = {}
        if 'company_name' in config:
            query_parmas['company'] = config['company_name']
        if 'node_name' in config:
            query_parmas['name'] = config['node_name']
        if 'external_ip' in config:
            query_parmas['ip'] = config['external_ip']
        if 'ip' in config:
            query_parmas['local_ip'] = config['ip']
        if 'anylog_server_port' in config:
            query_parmas['port'] = config['anylog_server_port']
        if 'anylog_rest_port' in config:
            query_parmas['rest_port'] = config['anylog_rest_port']
        if not policy_cmd.drop_policy(conn=conn, master_node=master_node, policy_type=config['node_type'], query_params=query_parmas, exception=exception):
            print('Failed to drop %s policy named: %s' % (config['node_type'], config['node_name']))