import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployments')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'python_rest'))

from anylog_connector import AnyLogConnector


def run_scheduler1(anylog_conn:AnyLogConnector, exception:bool=False):
    """

    """