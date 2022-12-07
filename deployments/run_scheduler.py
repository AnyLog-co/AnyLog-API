import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from anylog_connection import AnyLogConnection
import generic_get_calls
import generic_post_calls
import blockchain_calls

def run_scheduler(anylog_conn:AnyLogConnection, blockchain_source:str, blockchain_destination:str, sync_time:str,
                    ledger_conn:str, exception:bool=False):
    processes = generic_get_calls.get_processes(anylog_conn=anylog_conn, exception=exception)
    if processes['Scheduler']['Status'] == 'Not declared':
        generic_post_calls.run_scheduler(anylog_conn=anylog_conn, exception=exception)
    # check scheduler 1
    if '[1 (user)]' not in processes['Scheduler']['Details']:
        generic_post_calls.run_scheduler(anylog_conn=anylog_conn, schedule_number=1, exception=exception)

    if processes['Blockchain Sync']['Status'] == 'Not declared':
        blockchain_calls.blockchain_sync(anylog_conn=anylog_conn, blockchain_source=blockchain_source,
                                         blockchain_destination=blockchain_destination, sync_time=sync_time,
                                         ledger_conn=ledger_conn, exception=exception)