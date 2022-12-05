import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('anylog_pyrest')[0]

from anylog_connection import AnyLogConnection


def get_policy(anylog_conn:AnyLogConnection, policy_type:str, policy_name:str, member_type:str=None,
               company:str=None, exception:bool=False)->bool:
    """
    Check whether or not authentication policy exists
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog via REST
        policy_typs:str - policy type
        policy_name:str - policy name || user name for member policies
        member_type:str - for member policies the type
        company:str - company name
        exception:bool - whether or not to print exceptions
    :params:
        policy:dict - policy to return
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        policy
    """
    headers = { 
        'command': f'blockchain get {policy_type} where name={policy_name}',
        'User-Agent': 'AnyLog/1.23'
    }
    if member_type is not None: 
        headers['command'] += f' and type={member_type}'
    if company is not None:
        headers['command'] += f' and company={company}'

    r, error = anylog_conn.get(headers=headers)
    if r is False:
        policy = {}
        if exception is True:
            print_error(error_type='GET', cmd=headers['command'], error=error)
    else:
        try:
            policy = r.json()
        except:
            policy = {}

    return policy


def create_member_policy(member_type:str='user', member_name:str='user1', company:str=None)->dict:
    """
    Declare member policy
    :args:
        member_type:str - member type
        member_name:Str - name
        company:str - company
    :params:
        policy:dict - member policy as a dict
    :return:
        policy
    """
    policy = {
        "member": {
            'type': member_type,
            'name': member_name
        }
    }
    if company is not None:
        policy['member']['company'] = company

    return policy


