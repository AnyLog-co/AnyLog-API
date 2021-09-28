import os
import __init__
import anylog_api


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
    try:
        with open(deployment_file, 'r') as f:
            try:
                for line in f.readlines():
                    if not line.startswith('#') and not line.startswith('\n'):
                        r, error = conn.post(command=line.split('\n')[0])
                        if errors.post_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception):
                            status = False
            except Exception as e:
                status = False
                if exception is True:
                    print("Failed to read file '%s' (Error: %s)" % (deployment_file, e))
    except Exception as e:
        status = False
        if exception is True:
            print("failed to open file: '%s' (Error: %s)" % (deployment_file, e))

    return status



