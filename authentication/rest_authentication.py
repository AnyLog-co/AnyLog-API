import argparse
import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('authentication')[0]
KEYS_DIR = os.path.join(ROOT_DIR, 'authentication')
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from anylog_connection import AnyLogConnection
import anylog_pyrest.authentication as authentication
import authentication_user


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conn', type=str, default='127.0.0.1:32048', help='REST connection information')
    parser.add_argument('username', type=str, default='user1', help='Authentication username')
    parser.add_argument('--local-password', type=str, default='passwd', help='Node password')
    parser.add_argument('--password', type=str, default='demo', help='user password')
    parser.add_argument('--old-password', type=str, default=None, help='old user password if updating')
    parser.add_argument('--user-type', type=str, default='user', choices=['admin', 'user'], help='user type')
    parser.add_argument('--expiration', type=str, default=None, help='A time limit that terminates permissions for the user.')
    parser.add_argument('--add', type=bool, nargs='?', const=True, default=False, help='create a new user for REST authentication')
    parser.add_argument('--update', type=bool, nargs='?', const=True, default=False, help='update user password for REST authentication')
    parser.add_argument('--delete', type=bool, nargs='?', const=True, default=False, help='remove user from REST authentication')
    parser.add_argument('--auth', type=str, default=None, help='Authentication information (comma separated) [ex. username,password]')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = parser.parse_args()

    auth = None
    if args.auth is not None:
        auth = tuple(args.auth)

    anylog_conn = AnyLogConnection(conn=args.conn, auth=auth, timeout=args.timeout)

    if args.add is True:
        if authentication.set_local_password(anylog_conn=anylog_conn, password=args.password,
                                             exception=args.exception):
            if authentication.enable_authentication(anylog_conn=anylog_conn, authentication_type='user', enable=True,
                                                    exception=args.exception):
                if not authentication_user.add_user(anylog_conn=anylog_conn, username=args.username,
                                                    password=args.password, user_type=args.user_type,
                                                    expiration=args.expiration, exception=args.exception):
                    print(f'Failed to create {args.user_type} user {args.username} with password: {args.password}')
    elif args.update is True:
        if not authentication_user.update_password(anylog_conn=anylog_conn, username=args.username,
                                                   old_password=args.old_password, password=args.password,
                                                   exception=args.exception):
            print(f'Failed to update {args.username} with new password')
    elif args.delete is True:
        if not authentication_user.remove_user(anylog_conn=anylog_conn, username=args.username, exception=args.exception):
            print(f'Failed to remove user {args.username}')
    else:
        print('Missing process type')



if __name__ == '__main__':
    main()

