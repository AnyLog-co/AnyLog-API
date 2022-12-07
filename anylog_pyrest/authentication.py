from anylog_connection import AnyLogConnection
import generic_get_calls
import generic_post_calls
import support


def __key_vars(anylog_conn:AnyLogConnection, key_type:str, password:str=None, keys_file:str=None, exception:bool=False)->str:
    """
    Extract key
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        key_type:str - key type (private or public)
        password:str - password associated with keys
        keys_file:str - file associated with keys
        exception:bool - whether to print exceptions
    :params:
        param_name:str - AnyLog parameter name
        param_cmd:str - command to associate with AnyLog param
        options:str - where conditions
        configs:dict - configurations from AnyLog
    :return:
        key for
    """
    param_name = f'{key_type}_key'
    param_cmd = f'get {key_type} key'
    options = "where"
    if password is not None:
        if options == "where":
            options += f' password={password}'
        else:
            options += f' and password={password}'
    if keys_file is not None:
        if options == "where":
            options += f' keys_file={keys_file}'
        else:
            options += f' and keys_file={keys_file}'
    if options != "where":
        param_cmd += f' {options}'

    if generic_post_calls.add_param(anylog_conn=anylog_conn, key=param_name, value=param_cmd, exception=exception) is True:
        configs = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, exception=exception)
        if param_name in configs:
            return configs[param_name]


def enable_authentication(anylog_conn:AnyLogConnection, authentication_type:str, enable:bool=True, exception:bool=False)->bool:
    """
    Set authentication on/off for either node or user
    :args:
        anylog_conn:AnyLogConnection - connect to AnyLog node
        authentication_type:str - authentication type (node or user)
        enable:bool - whether to enable/disable authentication
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status = True
    headers = {
        'command': f'set {authentication_type} authentication',
        'User-Agent': 'AnyLog/1.23'
    }
    if enable is True:
        headers['command'] += ' on'
    elif enable is False:
        headers['command'] += ' off'

    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True:
            support.print_rest_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def set_local_password(anylog_conn:AnyLogConnection, password:str, exception:bool=False)->bool:
    """
    Declare local password
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        password:str - local password
        exception:bool - whether to print exception
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status = True
    headers = {
        'command': f'set local password={password}',
        'User-Agent': 'AnyLog/1.23'
    }

    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True:
            support.print_rest_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def create_keys(anylog_conn:AnyLogConnection, password:str=None, keys_file:str=None, exception:bool=False)->bool:
    """
    Create public and private keys
    :args:
        anylog_conn:AnyLogConnection - connect to AnyLog node
        password:str - password associated with keys
        keys_file:str - file associated with keys
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status=False
    headers = {
        'command': f'id create keys',
        'User-Agent': 'AnyLog/1.23'
    }
    options = "where"
    if password is not None:
        if options == "where":
            options += f' password={password}'
        else:
            options += f' and password={password}'
    if keys_file is not None:
        if options == "where":
            options += f' keys_file={keys_file}'
        else:
            options += f' and keys_file={keys_file}'
    if options != "where":
        headers['command'] += f' {options}'

    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True:
            support.print_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def get_keys(anylog_conn:AnyLogConnection, password:str=None, keys_file:str=None, exception:bool=False)->(str, str):
    """
    Get private and public keys from AnyLog
    :args:
        anylog_conn:AnyLogConnection - connect to AnyLog node
        password:str - password associated with keys
        keys_file:str - file associated with keys
    :params:
        private_key:str - private key
        public_key:str - public key
    :return:
        private and public keys
    """
    private_key = __key_vars(anylog_conn=anylog_conn, key_type='private', password=password, keys_file=keys_file,
                             exception=exception)
    public_key = __key_vars(anylog_conn=anylog_conn, key_type='public', password=password, keys_file=keys_file,
                             exception=exception)

    return private_key, public_key


def sign_policy(anylog_conn:AnyLogConnection, policy:str, password:str=None, exception:bool=False)->bool:
    status = True
    param_key = 'signed_policy'
    param_cmd = 'id sign !new_policy where key=!private_key'
    if password is not None:
        param_cmd += f' and password={password}'
    payload=f'<new_policy={policy}>'
    generic_post_calls.add_param(anylog_conn=anylog_conn, key=param_key, value=param_cmd, payload=payload,
                                 exception=exception)

