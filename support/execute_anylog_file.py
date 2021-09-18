import os

import __init__
import anylog_api

import errors


def __read_file(anylog_file:str)->list:
    """
    Read AnyLog filee
    :args:
        anylog_file:str - file to read
    :params:
        commands:list - list of commands from file
    :return:
        commands
    """
    commands = []
    anylog_file_path = os.path.expandvars(os.path.expanduser(anylog_file))
    if os.path.isfile(anylog_file_path):
        with open(anylog_file_path, 'r') as f:
            for line in f.readlines():
                if not line.startswith('#') and not line.startswith('\n'):
                    commands.append(line.split('\n')[0].split('#')[0])
    return commands


def execute_file(conn:anylog_api.AnyLogConnect, anylog_file:str, exception:bool=False)->bool:
    """
    Execute AnyLog file
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        anylog_file:str - file to execute
        exception:bool - whether to print excpetion
    :params:
        status:bool
        commands:list - commands to execute
    :return:
        status
    """
    status = True
    commands = __read_file(anylog_file=anylog_file)
    for cmd in commands:
        r, error = anylog_api.post(command=cmd)
        if not errors.get_error(conn=conn.conn, command=cmd, r=r, error=error, exception=exception):
            try:
                output = r.text
            except Exception as e:
                if exception is True:
                    print('Failed to excute command: %s (Error: %s)' % (cmd, e))
                status = False
    return status

