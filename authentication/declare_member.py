import argparse
import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('authentication')[0]
DIR_NAME = os.path.join(ROOT_DIR, 'authentication')
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from anylog_connection import AnyLogConnection
import authentication
import blockchain_authentication
import blockchain_calls
import support


def declare_member(anylog_conn:AnyLogConnection, member_type:str='user', member_name:str='admin', company:str=None,
                   password:str=None, private_key:bool=False, exception:bool=False):
    """
    Declare a member policy to blockchain
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        member_type:str - member type
        member_name:str - member name
        company:str - company associated with policy
        password:str - authentication password
        private_key:bool - whether private key exists on the node we're sending the request(s) against
            if private key  exists then it should be declared as a variable (!private_key) in the AnyLog dictionary
        exception:bool - whether or not to print exceptions
    :params:
        policy:dict - policy to post on the blockchain 
    """

    if member_type not in ['root', 'user', 'node']:
        member_type = 'user'

    # check if policy exists
    policy = blockchain_authentication.get_policy(anylog_conn=anylog_conn, policy_type='member', policy_name=member_name,
                                                  member_type=member_type, company=company, exception=exception)
    if policy != {}:
        print(f'Member policy for {member_type} {member_name} already exists')
        return

    policy = blockchain_authentication.create_member_policy(member_type=member_type, member_name=member_name,
                                                            company=company)

    policy = support.json_dumps(content=policy, exception=exception)

    policy = blockchain_calls.prep_policy(anylog_conn=anylog_conn, policy=policy, exception=exception)

    if policy != "":
        authentication.sign_message(anylog_conn=anylog_conn, message=policy, password=password,
                                    private_key=private_key, exception=exception)


if __name__ == '__main__':
    declare_member(anylog_conn=AnyLogConnection('10.0.0.226:32049'), member_type='root', member_name='admin',
                   company='AnyLog', password='demo', private_key=True, exception=True)