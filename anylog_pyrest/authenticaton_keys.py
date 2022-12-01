import os
import sys
ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('anylog_pyrest')[0]
DIR_NAME = os.path.join(ROOT_DIR, 'authentication')

from anylog_connection import AnyLogConnection
from generic_get_calls import get_dictionary
import support


def __private_key_var(anylog_conn:AnyLogConnection, password:str, keys_file:str=None, exception:bool=False)->bool:
    """
    set private to AnyLog variable
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog class
        password:str - authentication key password
        keys_file:str - file to store keys on AnyLog node (name only)
        exception:bool - whether or not print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    """
    status=True
    headers = {
        'command': f'private_key = get private key where password={password}',
        'User-Agent': 'AnyLog/1.23'
    }
    if keys_file is not None:
        headers['command'] += f' and keys_file={keys_file}'

    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True:
            support.print_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def __public_key_var(anylog_conn:AnyLogConnection, password:str, keys_file:str=None,
                      exception:bool=False)->bool:
    """
    set public to AnyLog variable
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog class
        password:str - authentication key password
        keys_file:str - file to store keys on AnyLog node (name only)
        exception:bool - whether or not print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    """
    status = True
    headers = {
        'command': f'public_key = get public key where password={password}',
        'User-Agent': 'AnyLog/1.23'
    }
    if keys_file is not None:
        headers['command'] += f' and keys_file={keys_file}'

    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True:
            support.print_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def __extract_keys(anylog_conn:AnyLogConnection, exception:bool=False)->(str, str):
    """
    Extract private and public keys
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog class
        exception:bool - whether or not print exceptions
    :params:
        configs:dict - AnyLog params dictionary
        private_key:str - extracted private key
        public_key:str - extract public key
    :return:
        private_key, public_key
    """
    private_key = ""
    public_key = ""
    configs = get_dictionary(anylog_conn=anylog_conn, exception=exception)

    if 'private_key' in configs:
        private_key = configs['private_key']
    if 'public_key' in configs:
        public_key = configs['public_key']

    return private_key, public_key


def __store_key(key:str, file_name:str, local_dir:str=DIR_NAME, exception:bool=False)->(str, str):
    """
    Store private and public keys in file
    :args:
        key;str - key to store
        file_name:str - file name to store key in 
        local_dir:str - dir to store content in
        exception:bool - whether or not to print exceptions
    :params:
        full_dir_path:str - expanded local_dir
        private_key_path:str - file path for private key
        public_key_path:str - file path for public key
    :return:
        path of private and public keys - if empty returns ""
    """
    full_dir_path = os.path.expandvars(os.path.expanduser(local_dir))
    private_key_path = ""
    public_key_path = ""

    if not os.path.isdir(full_dir_path):
        try:
            os.makedir(full_dir_path)
        except Exception as error:
            if exception is True:
                print(f'Failed to create directory {local_dir} (Error: {error})')
            return private_key_path, public_key_path
    
    key_path = os.path.join(full_dir_path, file_name)
    if support.generic_write(file_path=key_path, content=key, exception=exception) is False:
        key_path = ""

    return key_path


def declare_keys(anylog_conn:AnyLogConnection, password:str, keys_file:str=None, exception:bool=False)->bool:
    """
    Declare private and public key authentication
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog class
        password:str - authentication key password
        keys_file:str - file to store keys on AnyLog node (name only)
        exception:bool - whether or not print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    """
    status=False
    headers = {
        'command': f'id create keys where password={password}',
        'User-Agent': 'AnyLog/1.23'
    }
    if keys_file is not None:
        headers['command'] += f' and keys_file={keys_file}'

    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True:
            support.print_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def get_key(anylog_conn:AnyLogConnection, password:str, keys_file:str=None, local_dir:str=DIR_NAME,
            exception:bool=False)->(str, str):
    """
    Store keys to local file(s)
    :process:
        1. set private and public keys to AnyLog variables
        2. extract variables
        3. store to file
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog class
        password:str - authentication key password
        keys_file:str - file to store keys on AnyLog node (name only)
        local_dir:str - directory to store keys
        exception:bool - whether or not print exceptions
    :return:
        file name for both public and private keys
    """
    private_status = __private_key_var(anylog_conn=anylog_conn, password=password, keys_file=keys_file,
                                       exception=exception)
    public_status = __public_key_var(anylog_conn=anylog_conn, password=password, keys_file=keys_file,
                                       exception=exception)

    if private_status is False or public_status is False:
        return '', ''

    private_key, public_key = __extract_keys(anylog_conn=anylog_conn, exception=exception)
    private_key_path = __store_key(key=private_key, file_name='private_key.pem', local_dir=local_dir, exception=exception)
    public_key_path = __store_key(key=public_key, file_name='public_key.pem', local_dir=local_dir, exception=exception)
    
    return private_key_path, public_key_path




