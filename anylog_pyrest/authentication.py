from anylog_connection import AnyLogConnection
from support import print_error


def enable_authentication(anylog_conn:AnyLogConnection, auth_type:str='user', enable:bool=True,
                          exception:bool=False)->bool:
    """
    Whether or not to enable authentication
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        auth_type:str - user or node authentication
        enable:bool - If True enable authentication, if False disable
        exception:bool - whether or not to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status = True
    headers = {
        'command': f'set {auth_type} authentication ',
        'User-Agent': 'AnyLog/1.23'
    }

    if enable is True:
        headers['command'] += 'on'
    else:
        headers['command'] += 'off'

    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True:
            print_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def set_password(anylog_conn:AnyLogConnection, password:str, password_type:str="local", file_path:str=None,
                 exception:bool=False)->bool:
    """
    Set password
        if password_type == 'local': Provide a password to protect sensitive information that is kept on the node
        if password_type == 'private': Make the password protecting the private key available on the node.
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        password:str - password to encrypt with
        password_type:str - whether it's a public or private password
        file_path:str - if private, the file to encrypt
        exception:bool - whether or not to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status = True
    if password_type not in ['local', 'private']:
        password_type = 'local'
    headers = {
        'command': f'set {password_type} password={password}',
        'User-Agent': 'AnyLog/1.23'
    }

    if password_type == 'private' and file_path is not None:
        headers['command'] += f' {file_path}'

    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True:
            print_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def basic_add_user(anylog_conn:AnyLogConnection, name:str, password:str, user_type:str='user', expiration:str=None,
                   exception:bool=False)->bool:
    """
    Basic user authentication when doing cURL request
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/authentication.md#users-authentication
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog
        name:str - A unique name to identify the user
        password:str - Any character string
        user_type:str - The type of user, i.e. admin. The default value is user
        expiration:str - A time limit that terminates permissions for the user.
        exception:bool - whether or not to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
        r:bool, error:str - whether the command failed & why
    :return:
        status
    """
    status = True
    if user_type not in ['admin', 'user']:
        user_type = 'user'

    headers = {
        'command': f'id add user where name={name} and password={password} and type={user_type}',
        'User-Agent': 'AnyLog/1.23'
    }
    if expiration is not None:
        headers['command'] += f' expiration={expiration}'

    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True:
            print_error(error_type='POST', cmd=headers['command'], error=error)

    return status
