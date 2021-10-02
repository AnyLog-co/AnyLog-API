import __init__
import anylog_api
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

def disconnect_node(conn:anylog_api.AnyLogConnect, config:dict, drop_policy:bool=False, exception:bool=False):
    """
    Disconnect node from network. If drop_policy is True policy will be dropped
    Code does not drop table or cluster from ledger
    :args:
        conn:anylog_api.AnyLogConnect - connect to AnyLog
        config:dict - config from file

        drop_policy:bool - whether to drop policy
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
            print(process)
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
    # Drop policy
    if 'company_name' in config:
        if isinstance(value, str):
            value = value.replace('"', '').replace("'", "").lstrip().rstrip()
        stmt = '%s=%s'
        if isinstance(value, str) and (" " in value or "+" in value):
            stmt = '%s="%s"'
        while_conditions.append(stmt % (key, value))
    exit(1)
    #post_cmd.drop_policy(conn=conn, master_node=master_node, policy_type=config['node_type'], query_params:dict,
     #           exception:bool)->bool: