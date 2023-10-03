import os

from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.generic_post_calls import set_anylog_home, create_directories
ROOT_DIR = os.path.expanduser(os.path.expandvars(__file__)).split('python_main')[0]


def declare_directories(anylog_conn:AnyLogConnector=None, anylog_path:str=ROOT_DIR, exception:bool=False):
    """
    create AnyLog directories
    :args:
        anylog_path:str - AnyLog root path
        exceptions;bool - whether to print exceptions
    :params:
        status:bool - status
    """
    anylog_path = os.path.expandvars(os.path.expandvars(anylog_path))
    status = set_anylog_home(anylog_conn=anylog_conn, root_path=anylog_path, destination=None, view_help=False, exception=exception)
    if status is False:
        print(f"Failed to set {anylog_path} as home")
    else:
        if create_directories(anylog_conn=anylog_conn, destination=None, view_help=False, exception=exception) is False:
            print(f"Failed to create directories in {anylog_path}. Cannot continue...")
            status = False

    if status is False:
        exit(1)




