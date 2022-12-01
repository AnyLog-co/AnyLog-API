import argparse
import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('authentication')[0]
DIR_NAME = os.path.join(ROOT_DIR, 'authentication')
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from anylog_connection import AnyLogConnection
import create_keys

def main():
    """
    The following demonstrates using 
    ;process:
        1. set keys
        2. create member policy
        3. sign policy
        4. declare policy on blockchain
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('conn', type=str, default='127.0.0.1:32048', help='REST connection information')
    # parser.add_argument('root_user', type=str, default='admin', help='root user name')
    parser.add_argument('root_password', type=str, default='demo', help='RSA keys password')
    parser.add_argument('--keys-file', type=str, default='root', help='file to store keys on AnyLog node (name only)')
    parser.add_argument('--local-dir', type=str, default=create_keys.DIR_NAME, help='local directory to store root keys')
    parser.add_argument('--auth', type=str, default=None,
                        help='Authentication information (comma separated) [ex. username,password]')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = args = parser.parse_args()

    auth = None
    if args.auth is not None:
        auth = tuple(args.auth)
        
    anylog_conn = AnyLogConnection(conn=args.conn, auth=auth, timeout=args.timeout)

    # set authentication keys & store them locally
    create_keys.main(anylog_conn=anylog_conn, password=args.root_password, keys_file=args.keys_file,
                     local_dir=args.local_dir, exception=args.exception)

    # declare member policy

    # sign policy

    # post policy

if __name__ == '__main__':
    main()


