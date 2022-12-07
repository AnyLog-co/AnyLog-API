import argparse
import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('authentication')[0]
KEYS_DIR = os.path.join(ROOT_DIR, 'authentication')
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from anylog_connection import AnyLogConnection
import anylog_pyrest.authentication as authentication
import blockchain_calls
import blockchain_policies
import create_keys
import support

def declare_member(anylog_conn:AnyLogConnection, member_type:str, name:str, company:str=None, policy_id:str=None,
                   password:str=None, keys_file:str=None, local_dir:str=create_keys.KEYS_DIR, exception:bool=False):

    """
    declare root credentials for AnyLog
    :process:
        1. create keys (if DNE)  - if exist just moves on
        2. declare policy
        3. sign policy
        4. store signed policy on blockchain
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        member_type:str - member type (root, user, node)
        name:str - root username
        company:str - company root is associated with (optional)
        policy_id:str - ID for root policy
        password:str - authentication keys password
        keys_file:str - authentication keys file (name only)
        local_dir:str - directory to store keys locally
        exception:bool - whether to print exceptions
    """
    if blockchain_calls.get_policy(anylog_conn=anylog_conn, policy_type='member', name=name, company=company,
                                   member_type=member_type, exception=exception) == {}:

        policy = blockchain_policies.create_member_policy(member_type='root', name=name, company=company, id=policy_id)
        str_policy = support.json_dumps(contnet=policy, exception=exception)

        if authentication.sign_policy(anylog_conn=anylog_conn, policy=str_policy, password=password, exception=exception) is True:
            if blockchain_calls.post_signed_policy(anylog_conn=anylog_conn, policy_name='signed_policy', exception=exception) is False:
                print('Failed to declare root policy in blockchain')
        else:
            print('Failed to declare root policy in blockchain')




