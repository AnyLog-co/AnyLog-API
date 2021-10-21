import os
import __init__
import anylog_api
import blockchain_cmd
import dbms_cmd
import post_cmd


def deploy_file(conn:anylog_api.AnyLogConnect, deployment_file:str, exception:bool=False)->bool:
    """
    Deploy commands in file against AnyLog
    :args:
       conn:anylog_api.AnyLogConnect - Connection to AnyLog
       deployment_file:str - file with commands to execute
    :params:
        status:bool
        f:_io.TextIOWrapper - open deployment_file file
            line:str - line from file
        r:bool, error:str - error output against AnyLog command
    """
    deployment_file = os.path.expandvars(os.path.expanduser(deployment_file))
    errors = {}
    status = True
    deployment_file = os.path.expanduser(os.path.expandvars(deployment_file))
    if os.path.isfile(deployment_file):
        try:
            with open(deployment_file, 'r') as f:
                try:
                    for line in f.readlines():
                        if not line.startswith('#'):
                            new_line = line.split('\n')[0]
                            status = post_cmd.generic_post(conn=conn, command=new_line, exception=exception)
                except Exception as e:
                    status = False
                    if exception is True:
                        print('Failed to read file %s (Error: %s)' % (deployment_file, e))
        except Exception as e:
            status = False
            if exception is True:
                print('Failed to open file: %s (Error: %s)' % (deployment_file, e))
    else:
        status = False
        if exception is True:
            print('Failed to locate file: %s' % deployment_file)

    return status



