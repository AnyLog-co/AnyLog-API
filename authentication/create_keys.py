import argparse
import os
import sys

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('authentication')[0]
KEYS_DIR = os.path.join(ROOT_DIR, 'authentication')
sys.path.insert(0, os.path.join(ROOT_DIR, 'anylog_pyrest'))

from anylog_connection import AnyLogConnection
import anylog_pyrest.authentication as authentication
import support


def generate_keys(anylog_conn:AnyLogConnection, password:str=None, keys_file:str=None,
                  local_dir: str = KEYS_DIR, exception:bool=False):
    """
    Generate keys and store them locally
    :steps;
        1. check if keys already exist
        2. create keys if (at least 1) DNE
        3. extract keys to local file
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        password:str - authentication keys password
        keys_file:str - authentication keys file (name only)
        local_dir:str - directory to store keys locally
        exception:bool - whether to print exceptions
    :params:
        private_key:str - path of local private key
        public_key:str - path of local public key
        file_name:str - file to store credentials in
    """
    # check if keys exist
    private_key, public_key = authentication.get_keys(anylog_conn=anylog_conn, password=password, keys_file=keys_file,
                                                      exception=exception)

    # create keys if DNE
    while private_key is None or public_key is None:
        if authentication.create_keys(anylog_conn=anylog_conn, password=password, keys_file=keys_file, exception=exception) is True:
            private_key, public_key = authentication.get_keys(anylog_conn=anylog_conn, password=password,
                                                                        keys_file=keys_file, exception=exception)

    # store keys locally
    if local_dir is not None:
        if private_key is not None:
            key_name = 'private_key.pem'
            if keys_file is not None:
                key_name = f'{keys_file.strip().replace(" ", "_")}_private_key.pem'
            if local_dir is not None:
                file_name = os.path.join(local_dir, key_name)
                support.generic_write(file_path=file_name, content=private_key, exception=exception)
        if public_key is not None:
            key_name = 'public_key.pem'
            if keys_file is not None:
                key_name = f'{keys_file.strip().replace(" ", "_")}_public_key.pem'
            if local_dir is not None:
                file_name = os.path.join(local_dir, key_name)
                support.generic_write(file_path=file_name, content=public_key, exception=exception)


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
    parser.add_argument('--local-dir', type=str, default=KEYS_DIR, help='local directory to store root keys')
    parser.add_argument('--auth', type=str, default=None, help='Authentication information (comma separated) [ex. username,password]')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = args = parser.parse_args()

    auth = None
    if args.auth is not None:
        auth = tuple(args.auth)

    anylog_conn = AnyLogConnection(conn=args.conn, auth=auth, timeout=args.timeout)
    generate_keys(anylog_conn=anylog_conn, password=args.password, keys_file=args.keys_file, local_dir=args.local_dir,
                  exception=args.exception)