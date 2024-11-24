from itertools import count

import anylog_api.anylog_connector as anylog_connector
import anylog_api.blockchain.cmds as blockchain_cmds
from anylog_api.generic.get import get_hostname, get_help
import anylog_api.generic.monitoring as monitoring_cmd
from anylog_api.generic.scheduler import run_schedule_task
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.blockchain.cmds import get_policy


def __monitoring_cmds(conn:anylog_connector.AnyLogConnector, exception:bool=False):
    script = []

    # prepare commands
    get_query_nodes = get_policy(conn=conn, policy_type='query', bring_case="ip_port", view_help=False,
                                 return_cmd=True, exception=exception)
    node_insight = monitoring_cmd.get_node_stats(conn=conn, json_format=True, destination=None, view_help=False,
                                                     return_cmd=True, exception=exception)
    node_name = get_hostname(conn=conn, destination=None, view_help=False, return_cmd=True, exception=exception)
    free_space = monitoring_cmd.get_disk_space(conn=conn, param='percentage', path='.', json_format=False,
                                               destination=None, view_help=False, return_cmd=True, exception=exception)
    cpu_percent = monitoring_cmd.get_node_info(conn=conn, attribute_function='cpu_percent', destination=None,
                                               view_help=False, return_cmd=True, exception=exception)
    packets_recv = monitoring_cmd.get_node_info(conn=conn, attribute_function='net_io_counters',
                                                attribute='packets_recv',view_help=False, return_cmd=True, exception=exception)
    packets_sent = monitoring_cmd.get_node_info(conn=conn, attribute_function='net_io_counters', attribute='packets_sent',
                                                destination=None, view_help=False, return_cmd=True, exception=exception)
    errin = monitoring_cmd.get_node_info(conn=conn, attribute_function='net_io_counters', attribute='errin',
                                         destination=None, view_help=False, return_cmd=True, exception=exception)
    errout = monitoring_cmd.get_node_info(conn=conn, attribute_function='net_io_counters', attribute='errout',
                                          destination=None, view_help=False, return_cmd=True, exception=exception)


    # generate schedule process
    new_schedule_process = run_schedule_task(conn=conn, name='monitoring_ips', time_interval='300 seconds',
                                             task=f'monitoring_ips={get_query_nodes}', destination=None, view_help=False,
                                             return_cmd=True, exception=exception)
    script.append(new_schedule_process)

    new_schedule_process = run_schedule_task(conn=conn, name='node_insight', time_interval='30 seconds',
                                             task=f'node_insight={node_insight}', destination=None, view_help=False,
                                             return_cmd=True, exception=exception)
    script.append(new_schedule_process)

    new_schedule_process = run_schedule_task(conn=conn, name='node_name', time_interval='30 seconds',
                                             task=f'node_insight[Node name]={node_name}', destination=None, view_help=False,
                                             return_cmd=True, exception=exception)
    script.append(new_schedule_process)

    new_schedule_process = run_schedule_task(conn=conn, name='disk_space', time_interval='30 seconds',
                                             task=f'node_insight[Free space %]={free_space}', destination=None,
                                             view_help=False,
                                             return_cmd=True, exception=exception)
    script.append(new_schedule_process)

    new_schedule_process = run_schedule_task(conn=conn, name='cpu_percent', time_interval='30 seconds',
                                             task=f'node_insight[CPU %]={cpu_percent}', destination=None,
                                             view_help=False,
                                             return_cmd=True, exception=exception)
    script.append(new_schedule_process)

    new_schedule_process = run_schedule_task(conn=conn, name='packets_recv', time_interval='30 seconds',
                                             task=f'node_insight[Packets Recv]={packets_recv}', destination=None,
                                             view_help=False,
                                             return_cmd=True, exception=exception)
    script.append(new_schedule_process)

    new_schedule_process = run_schedule_task(conn=conn, name='packets_sent', time_interval='30 seconds',
                                             task=f'node_insight[Packets Sent]={packets_sent}', destination=None,
                                             view_help=False,
                                             return_cmd=True, exception=exception)
    script.append(new_schedule_process)

    new_schedule_process = run_schedule_task(conn=conn, name='errin', time_interval='30 seconds',
                                             task=f'errin={errin}', destination=None,
                                             view_help=False,
                                             return_cmd=True, exception=exception)
    script.append(new_schedule_process)

    new_schedule_process = run_schedule_task(conn=conn, name='errout', time_interval='30 seconds',
                                             task=f'errout={errout}', destination=None,
                                             view_help=False,
                                             return_cmd=True, exception=exception)
    script.append(new_schedule_process)

    new_schedule_process = run_schedule_task(conn=conn, name='error_count', time_interval='30 seconds',
                                             task=f'node_insight[Network Error] = python int(!errin) + int(!errout)',
                                             destination=None, view_help=False, return_cmd=True, exception=exception)
    script.append(new_schedule_process)

    new_schedule_process = run_schedule_task(conn=conn, name='monitor_node', time_interval='30 seconds',
                                             task=f'if !monitoring_ips then run client (!monitoring_ips) monitor operators where info = !node_insight',
                                             destination=None, view_help=False, return_cmd=True, exception=exception)
    script.append(new_schedule_process)

    return script


def monitoring_policy(conn:anylog_connector.AnyLogConnector, ledger_conn:str, destination:str=None, view_help:bool=False,
                       return_cmd:bool=False, exception:bool=False):
    scripts = __monitoring_cmds(conn=conn, exception=exception)
    policy_id = None
    counter = 0
    new_policy = {
        "schedule": {
            'name': 'Generic Monitoring Schedule',
            'script': scripts
        }
    }

    while not policy_id and counter < 2:
        policy_id = blockchain_cmds.get_policy(conn=conn, policy_type='schedule',
                                               where_condition='name="Generic Monitoring Schedule"', bring_case="first",
                                               bring_condition="[*][id]", destination=destination, view_help=view_help,
                                               return_cmd=return_cmd, exception=exception)
        if not policy_id and counter == 0:
            blockchain_cmds.prepare_policy(conn=conn, policy=new_policy, destination=destination, view_help=view_help,
                                           return_cmd=return_cmd, exception=exception)
            blockchain_cmds.post_policy(conn=conn, policy=new_policy, ledger_conn=ledger_conn,
                                        destination=destination, view_help=view_help, return_cmd=return_cmd,
                                        exception=exception)
            counter += 1
        elif not policy_id:
            print(f"Failed to declare monitoring policy against {ledger_conn}, cannot continue...")
            exit(1)

    if policy_id:
        blockchain_cmds.config_from_policy(conn=conn, policy_id=policy_id, destination=destination, view_help=view_help,
                                           return_cmd=return_cmd, exception=exception)
    else:
        print("Failed to locate policy ID, cannot configure from policy")



def execute_monitering(conn:anylog_connector.AnyLogConnector, destination:str=None, view_help:bool=False,
                       return_cmd:bool=False, exception:bool=False):
    scripts = __monitoring_cmds(conn=conn, exception=exception)
    headers = {
        "command": None,
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination

    for script in scripts:
        headers['command'] = script
        if view_help is True:
            get_help(conn=conn, cmd=headers['command'], exception=exception)
        if return_cmd is True:
            status = headers['command']
        elif view_help is False:
            status = execute_publish_cmd(conn=conn, cmd='POST', headers=headers, payload=None, exception=exception)