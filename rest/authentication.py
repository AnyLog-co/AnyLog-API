"""
Link: https://github.com/AnyLog-co/documentation/blob/master/authentication.md
"""
import import_packages
import_packages.import_dirs()

import anylog_api
import other_cmd
import post_cmd

HEADER = {
    "command": None,
    "User-Agent": "AnyLog/1.23"
}


def set_authentication_off(conn:anylog_api.AnyLogConnect, exception:bool=False)->bool:
    """
    Set authentication off - Authentication is off by default when deploying AnyLog
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        status:bool
        HEADER:dict - header for POST request
    :return:
        status - True if no issues
    """
    status = True
    HEADER['command'] = "set authentication off"
    r, error = conn.post(headers=HEADER)
    if other_cmd.print_error(conn=conn.conn, request_type="post", command=HEADER['command'], r=r, error=error, exception=exception):
        status = False
    return status

def set_user_authentication_on(conn:anylog_api.AnyLogConnect, user_password:str, exception:bool=False)->bool:
    """
    Set authentication off - Authentication is off by default when deploying AnyLog
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        status:bool
        HEADER:dict - header for POST request
    :return:
        status - True if no issues
    """
    status = True
    HEADER['command'] = "user authentication on where password=%s" % user_password
    r, error = conn.post(headers=HEADER)
    if other_cmd.print_error(conn=conn.conn, request_type="post", command=HEADER['command'], r=r, error=error, exception=exception):
        status = False
    return status


def get_users(conn:anylog_api.AnyLogConnect, user_name:str, exception:bool=False)->bool:
    """
    Check whether user exists
    :args:
        conn:anylog_api.AnyLogConnct - connection to AnyLog via REST
        user_name:str - A unique name to identify the user
        excepton:bool - whether to print exception
    :params:
        status:bool
    :return:
        if user DNE or fails to return results return False, else return True
    """
    status = False
    headers = {
        'command': 'get users',
        'User-Agent': 'AnyLog/1.23'
    }

    r, error = conn.get(headers=HEADER)

    # Validate doesn't fail
    if other_cmd.print_error(conn=conn.conn, request_type="get", command="get users", r=r, error=error, exception=exception):
        status = True
    else:
        try:
            print(r)
        except Exception as e:
            print(e)

    return status

def set_user_authenticaton(conn:anylog_api.AnyLogConnect, user_name:str, user_password:str, user_type:str='user',
                           expiration:str=None, exception:bool=False)->bool:
    """
    Users names and passwords are added to each node to only allow connections with permitted users.
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/authentication.md#add-users
    :args:
        conn:anylog_api.AnyLogConnct - connection to AnyLog via REST
        user_name:str - A unique name to identify the user
        user_password:str - Password correlated to a user
        user_type:str - The type of user, i.e. admin. The default value is user
        expiration:str - A time limit that terminates permissions for the user
        excepton:bool - whether to print exception
    :params:
        status:bool
        cmd:str - `id add user` command to add
    :return:
        status
    """
    status = True
    cmd = "id add user where name=%s and password=%s and type=%s" % (user_name, user_password, user_type)
    if expiration is not None:
        cmd += " and expiration=%s" % expiration

    r, error = post_cmd.generic_post(conn=conn, command=cmd, exception=exception)

    if other_cmd.print_error(conn=conn.conn, request_type='post', command=cmd, r=r, error=error, excepton=exception):
        status = False

    return status
