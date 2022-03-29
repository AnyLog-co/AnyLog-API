"""
1. Start Master node on desired node -- master.py
"""
import argparse
import json
import os
import sys
import time

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).split('anylog_scripts')[0]
REST_PATH = os.path.join(ROOT_PATH, 'anylog_pyrest')
sys.path.insert(0, REST_PATH)

from anylog_connection import AnyLogConnection
import authentication
import blockchain_calls
import database_calls
import deployment_calls
import generic_get_calls
import generic_post_calls


def __prep_policies(anylog_conn:AnyLogConnection, exception:boo=False)->list:
    """
    From original master, extract all policies except master and prep them to be inserted into a new master
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        policies:list - list of policies to transfer
    :return:
        policies
    """
    policies = blockchain_calls.blockchain_get(anylog_conn=anylog_conn, policy_type='*', where_condition=None,
                                               bring_condition=None, separator=None, exception=args.exception)

    for policy in policies:
        policy_type = list(policy)[0]
        if policy_type == 'master':
            del policies[policies.index(policy)]
        else:
            for key in ['date', 'ledger', 'status']:
                try:
                    del policy[policy_type][key]
                except:
                    pass
    return policies


def __post_policies(anylog_conn:AnyLogConnection, policies:list, master_node:str, exception:bool=False)->bool:
    """
    Given a list of policies insert them into a new master node ledger
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        policies:list - list of policies to transfer
        master_node:str - master node to send policy tos
        exception:bool - whether to print exception
    :params:
        statuses:dict - policy / status relation
        status:bool
        policy:dict - specific policy (from policies) to transfer
        payload:str - policy converted to string
        headers:dict - REST header
        r:bool, error:str - whether the command failed & why
    :return:
        if at least 1 policy failed to POST, return False, else return True
    """
    statuses = {}
    for policy in policies:
        status = True
        try:
            payload = f"<new_policy={json.dumps(policy)}>"
        except Exception as e:
            status = False
            if exception is True:
                print(f"Failed to convert {policy} to string (Error: {e})")
        if status is True:
            headers = {
                "command": "blockchain prepare policy !new_policy",
                "User-Agent": "AnyLog/1.23"
            }
            r, error = anylog_conn.post(headers=headers, payload=payload)
            if r is False:
                status = False
                if exception is True:
                    print(f"Failed to prepare '{payload}' (Error {e})")
        if status is True:
            headers = {
                "command": f"blockchain insert where policy=!new_policy and local=true and master={master_node}",
                "User-Agent": "AnyLog/1.23"
            }
            r, error = anylog_conn.post(headers=headers, payload=payload)
            if r is False:
                status = False
                if exception is True:
                    print(f"Failed to insert '{payload}' (Error {e})")
        statuses[payload] = status

    if False in statuses.values():
        status = False
        if exception is True:
            for payload in statuses:
                if statuses[payload] is False:
                    print(f'Payload: {payload} - Failed')
    return status

def main():
    """
    The following is intended to provide support for transfering policies from one blockchian to another
    :process:
        0. A new master_node is up and running - AnyLog-API/anylog_scripts/master.py
        1. exit synchronizer
        2. exit blockchain database
        3. get policies
        4. clean results from policies
        5. insert policies into new database
        6. enable blockchain sync against new master
        [7. once the user can validate that (new) blockchain has been set, they can drop the old blockchain database]
            * connect to postgres database if blockchain was originally using psql
                connect dbms postgres where type=psql and ip={db_ip} and port={db_port} and user={db_user} and password={db_passwd}
            * drop database
                drop dbms blockchain from {db_type}
            * disconnect postgres if blockchain was originally using it
                disconnect dbms postgres
    :optional arguments:
        -h, --help                              show this help message and exit
        --master-node       MASTER_NODE         (New) Master Node REST IP:PORT      [default: 127.0.0.1:2149]
        --master-auth       MASTER_AUTH         Authentication (user, passwd)       [default: ()]
        --master-tcp        MASTER_TCP          (New) Master Node TCP IP:PORT       [default: 127.0.0.1:2148]
        --orig-master       ORIG_MASTER         Original Master Node REST IP:PORT   [default: 127.0.0.1:32149]
        --orig-master-auth  ORIG_MASTER_AUTH    Authentication (user, passwd) for original master node  [default: ()]
        --timeout           TIMEOUT             REST timeout                        [default: 30]
        --exception         EXCEPTION           whether to print exception          [default: False]
    :params:
        master_node:AnyLogConnection - connection to the new master node
        orig_master:AnyLogConnection  - connection to the original master node
        policies:list - list of policies to migrate from one ledger to another
    """
    parser = argparse.ArgumentParser()
    # new master node
    parser.add_argument('--master-node', type=str, default='127.0.0.1:2149', help='(New) Master Node REST IP:PORT')
    parser.add_argument('--master-auth', type=tuple, default=(), help='Authentication (user, passwd)')
    parser.add_argument('--master-tcp', type=str, default='127.0.0.1:2148', help='(New) Master Node TCP IP:PORT')
    # old master node
    parser.add_argument('--orig-master', type=str, default='127.0.0.1:32149', help='Original Master Node REST IP:PORT')
    parser.add_argument('--orig-master-auth', type=tuple, default=(), help='Authentication (user, passwd) for original master node')
    # other
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('--exception', type=bool, nargs='?', const=True, default=False, help='whether to print exception')
    args = parser.parse_args()

    master_node = AnyLogConnection(conn=args.master_node, auth=args.master_auth, timeout=args.timeout)
    orig_master_node = AnyLogConnection(conn=args.orig_master, auth=args.orig_master_auth, timeout=args.timeout)

    print("Validate Connection")
    for anylog_conn in [master_node, orig_master_node]:
        if not generic_get_calls.validate_status(anylog_conn=anylog_conn, exception=args.exception):
            print(f'Failed to connect to {anylog_conn}, cannot continue.')
            exit(1)

    print('Stop blockchain synchronizer')
    get_process = generic_get_calls.get_processes(anylog_conn=anylog_conn, exception=args.exception)
    count = 0
    while get_process['Blockchain Sync'] != 'Not declared' and count < 10:
        generic_post_calls.exit_cmd(anylog_conn=anylog_conn, process='synchronizer', exception=args.exception)
        get_process = generic_get_calls.get_processes(anylog_conn=anylog_conn, exception=args.exception)
        count += 1
    if count == 10 or get_process['Blockchain Sync'] != 'Not declared':
        print('Warning: Failed to stop blockchain synchronizer, this can cause issue during sync process')

    print('Disconnect blockchain logical database')
    database_calls.disconnect_dbms(anylog_conn=orig_master_node, db_name='blockchain', )

    # From original master_node get all policies
    print("Migrate Policies")
    policies = __prep_policies(anylog_conn=orig_master_node, exception=args.exception)

    # migrate policies from one master to another
    __post_policies(anylog_conn=master_node, policies=policies, master_node=args.master_tcp, exception=args.exception)

    print('Enable New Sync')
    sync_time = generic_get_calls.get_dictionary(anylog_conn=orig_master_node, exception=exception)['sync_time']
    generic_post_calls.blockchain_sync_scheduler(anylog_conn=orig_master_node, source="master", time=sync_time,
                                                 dest="file", connection=args.master_tcp, exception=args.exception)


if __name__ == '__main__':
    main()