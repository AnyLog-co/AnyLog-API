from anylog_connection import AnyLogConnection
import support


def add_user(anylog_conn:AnyLogConnection, username:str,  password:str, user_type:str='user', expiration:str=None,
             exception:bool=False)->bool:
    """
    Set REST authentication on a given node
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/authentication.md#users-authentication
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        username:str - A unique name to identify the user.
        password:str - Any character string
        type:str - The type of user, i.e. admin. The default value is user.
        expiration:str - A time limit that terminates permissions for the user.
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
        'command': f'id add user where name={username} and type={user_type} and password={password}',
        'User-Agent': 'AnyLog/1.23'
    }
    if expiration is not None:
        headers['command'] += f' and expiration={expiration}'

    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True:
            support.print_rest_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def update_user(anylog_conn:AnyLogConnection, username:str,  old_password:str, new_password:str, exception:bool=False)->bool:
    """
    Update password
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        username:str - A unique name to identify the user.
        old_password:str - old password
        new_password:str - new password
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
        'command': f'id update user where name={username} and old={old_password} and new={new_password}',
        'User-Agent': 'AnyLog/1.23'
    }

    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True:
            support.print_error(error_type='POST', cmd=headers['command'], error=error)

    return status


def remove_user(anylog_conn:AnyLogConnection, username:str, exception:bool=False)->bool:
    """
    remove existing user
    :args:
        anylog_conn:AnyLogConnection - connection to AnyLog node
        username:str - A unique name to identify the user.
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
        'command': f'id remove user where name={username}',
        'User-Agent': 'AnyLog/1.23'
    }

    r, error = anylog_conn.post(headers=headers)
    if r is False:
        status = False
        if exception is True:
            support.print_error(error_type='POST', cmd=headers['command'], error=error)

    return status
