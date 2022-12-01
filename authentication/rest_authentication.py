import argparse
import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('authentication')[0]
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from anylog_connection import AnyLogConnection
from generic_get_calls import validate_status
from authentication import basic_add_user, enable_authentication, set_password


def __validate_status(anylog_conn:AnyLogConnection, exception:bool=False):
    # validate current rest connection works
    status = validate_status(anylog_conn=anylog_conn, exception=exception)
    if status is True:
        print(f'Connection with {anylog_conn.conn} and Authentication {anylog_conn.auth} - Success')
    if status is False:
        print(f'Connection with {anylog_conn.conn} and Authentication {anylog_conn.auth} - Fails')

def main():
    """
    The following demonstrates a basic user authentication, where ultimately REST requests require username/password
    credentials to execute
    :process:
        1. set password
        2. enable user authentication
        3. set user authentication
    :positional arguments:
        conn                  REST connection information
        user_name             username to set for REST authentication
        user_password         password associate with user

    :optional arguments:
        -h, --help              show this help message and exit
        --user-type             user type (default: admin)
            * admin
            * user
        --expiration    EXPIRATION      time limit that terminates permissions for the user (example: 2 hours) (default: None)
        --auth          AUTH            Authentication information (comma separated) [ex. username,password] (default: None)
        --timeout       TIMEOUT         REST timeout (default: 30)
        -e, --exception [EXCEPTION]     Whether to print errors (default: False
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('conn', type=str, default='127.0.0.1:32048', help='REST connection information')
    parser.add_argument('user_name', type=str, default='user1', help='username to set for REST authentication')
    parser.add_argument('user_password', type=str, default='demo', help='password associate with user')
    parser.add_argument('--user-type', type=str, default='admin', choices=['admin', 'user'], help='user type')
    parser.add_argument('--expiration', type=str, default=None, help='time limit that terminates permissions for the user (example: 2 hours)')
    parser.add_argument('--auth', type=str, default=None, help='Authentication information (comma separated) [ex. username,password]')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = args = parser.parse_args()

    auth = args.auth
    if auth is not None:
        auth = tuple(auth)

    # validate node is accessible with existing credentials
    anylog_conn = AnyLogConnection(conn=args.conn, auth=auth, timeout=args.timeout)
    __validate_status(anylog_conn=anylog_conn, exception=args.exception)

    # add user
    if set_password(anylog_conn=anylog_conn, password=args.user_password, password_type='local',
                    file_path=None, exception=args.exception):
        if enable_authentication(anylog_conn=anylog_conn, auth_type='user', enable=True, exception=args.exception):
            if basic_add_user(anylog_conn=anylog_conn, name=args.user_name, password=args.user_password,
                              user_type=args.user_type, expiration=args.expiration, exception=args.exception) is True:
                auth = (args.user_name, args.user_password)
                anylog_conn = AnyLogConnection(conn=args.conn, auth=auth, timeout=args.timeout)
                # validate node is accessible with new credentials
                __validate_status(anylog_conn=anylog_conn, exception=args.exception)


if __name__ == '__main__':
    main()
