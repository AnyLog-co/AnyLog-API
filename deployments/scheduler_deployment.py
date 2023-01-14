import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'python_rest'))

from anylog_connector import AnyLogConnector
import generic_get_calls
import generic_post_calls
import blockchain_calls


def run_scheduler1(anylog_conn:AnyLogConnector, exception:bool=False)->bool:
    """
    Execute `run scheduler 1`
    :args:
        anylog_conn:AnyLogConnector - REST connection to AnyLog node
        exception:bool - whether to print exceptions
    :params:
        status:bool
        processes:dict - list of processes
    :return:
        status
    """
    status = True
    processes = generic_get_calls.get_processes(anylog_conn=anylog_conn, json_format=True, exception=exception)
    if '[1 (user)]' not in processes['Scheduler']['Details']:
        status = generic_post_calls.run_scheduler_1(anylog_conn=anylog_conn, exception=exception)

    if status is False:
        print('Error: Failed to start `run scheduler 1`. Cannot continue')

    return status


def run_blockchain_sync(anylog_conn:AnyLogConnector, anylog_configs:dict, exception:bool=False)->bool:
    status = True
    processes = generic_get_calls.get_processes(anylog_conn=anylog_conn, json_format=True, exception=exception)
    for param in ['ledger_conn', 'sync_time', 'blockchain_source', 'blockchain_destination']:
        if param not in anylog_configs:
            status = False

    if processes['Blockchain Sync']['Status'] == 'Not declared' and status is True:
        status = blockchain_calls.blockchain_sync(anylog_conn=anylog_conn,
                                                  blockchain_source=anylog_configs['blockchain_source'],
                                                  blockchain_destination=anylog_configs['blockchain_destination'],
                                                  sync_time=anylog_configs['sync_time'],
                                                  ledger_conn=anylog_configs['ledger_conn'], exception=exception)

    if status is False and 'ledger_conn' in anylog_configs:
        print(f'Failed to execute `blockchain sync` against master: {anylog_configs["ledger_conn"]}')
    elif status is False:
        print(f'Failed to execute `blockchain sync`')

    return status
