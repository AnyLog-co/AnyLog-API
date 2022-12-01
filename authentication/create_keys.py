import argparse
import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('authentication')[0]
DIR_NAME = os.path.join(ROOT_DIR, 'authentication')
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from anylog_connection import AnyLogConnection
import authentication
import authenticaton_keys


def __print_file_info(key_path:str, key_type:str):
    output = f"{key_type.title()} Key location: {key_path}"
    if key_path == "":
        output = f"Failed to store {key_type} Key locally"
    print(output)


def main(anylog_conn:AnyLogConnection, password:str, keys_file:str='root', local_dir:str=DIR_NAME, exception:bool=False):
    """
    Sample code to create private and public key, storing it both on node (in AnyLog-Network/anylog) and locally
    :args:
        anylog_conn:AnyLogConnection - REST connection to AnyLog
        password        RSA keys password
        keys_file           file to store keys on AnyLog node (name only) (default: root)
        local_dir           local directory to store root keys (default: /Users/orishadmon/AnyLog-API/authentication)
        exception           Whether to print errors (default: False)
    :params:
        private_key_path:str - path of private key
        public_key_path:str - path of public key
    """
    private_key_path, public_key_path = authenticaton_keys.get_key(anylog_conn=anylog_conn, password=password,
                                                                   keys_file=keys_file, local_dir=local_dir,
                                                                   exception=exception)

    while private_key_path == "" and public_key_path == "":
        # create keys if DNE
        if authenticaton_keys.declare_keys(anylog_conn=anylog_conn, password=password, keys_file=keys_file,
                                         exception=exception) is True:
            print(f'Failed to declare authentication keys against {anylog_conn.conn}')

        # store authentication keys locally
        private_key_path, public_key_path = authenticaton_keys.get_key(anylog_conn=anylog_conn, password=password,
                                                                        keys_file=keys_file, local_dir=local_dir,
                                                                        exception=exception)

    __print_file_info(key_path=private_key_path, key_type='private')
    __print_file_info(key_path=public_key_path, key_type='public')


if __name__ == '__main__':
    """
    :positional arguments:
        conn                  REST connection information
        root_password         RSA keys password
    :optional arguments:
        -h, --help                  show this help message and exit
        --keys-file     KEYS_FILE   file to store keys on AnyLog node (name only) (default: root)
        --local-dir     LOCAL_DIR   local directory to store root keys (default: /Users/orishadmon/AnyLog-API/authentication)
        --auth          AUTH        Authentication information (comma separated) [ex. username,password] (default: None)
        --timeout       TIMEOUT     REST timeout (default: 30)
        -e, --exception [EXCEPTION] Whether to print errors (default: False)
    :params: 
        auth:tuple - Authentication
        anylog_conn:AnyLogConnection - REST connection to AnyLog
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('conn', type=str, default='127.0.0.1:32048', help='REST connection information')
    parser.add_argument('password', type=str, default='demo', help='RSA keys password')
    parser.add_argument('--keys-file', type=str, default='root', help='file to store keys on AnyLog node (name only)')
    parser.add_argument('--local-dir', type=str, default=DIR_NAME, help='local directory to store root keys')
    parser.add_argument('--auth', type=str, default=None, help='Authentication information (comma separated) [ex. username,password]')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = args = parser.parse_args()

    auth = None
    if args.auth is not None:
        auth = tuple(args.auth)

    anylog_conn = AnyLogConnection(conn=args.conn, auth=auth, timeout=args.timeout)

    main(anylog_conn=anylog_conn, password=args.password, keys_file=args.keys_file, local_dir=args.local_dir, exception=args.exception)
    

