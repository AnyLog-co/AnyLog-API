import argparse
import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('authentication')[0]
DIR_NAME = os.path.join(ROOT_DIR, 'authentication')
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from anylog_connection import AnyLogConnection
import authentication
import authenticaton_keys


def declare_member(anylog_conn:AnyLog)