import argparse
import re


def check_conn_format(conn_ip_port:str, is_argpase:bool=True, exception:bool=False)->str:
    """
    Check format for connection information
    :args:
        conn_ip_port:str - connection information
        is_argpase:bool - (by default) if fails return argparse error
        exception:bool - print exception (when is_argpase is false)
    :params:
        pattern1:str - 127.0.0.1:32048
        pattern2:str - user:passwd@127.0.0.1:32048
    :return:
        conn_ip_port or None if fails
    """
    pattern1 = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$'
    pattern2 = r'^[a-zA-Z0-9]+:[a-zA-Z0-9]+@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$'

    if not re.match(pattern1, conn_ip_port) and not re.match(pattern2, conn_ip_port):
        if is_argpase is True:
            raise argparse.ArgumentError(None, "Invalid connection information format. Valid Formats `127.0.0.1:32048` and `user:password@127.0.0.1:32048`")
        else:
            conn_ip_port = None
            if exception is True:
                print("Invalid connection information format. Valid Formats `127.0.0.1:32048` and `user:password@127.0.0.1:32048`")

    return conn_ip_port


def extract_conn_information(conn_ip_port:str)->(str, tuple):
    """
    given connection information separate credentials form ip and port
    :args:
        conn_ip_port:str - connection information
    :params:
        conn:str - IP and port
        auth:tuple -  credentials
    :return:
        conn, auth
    """
    conn = conn_ip_port
    auth = ()
    if '@' in conn_ip_port:
        auth, conn = conn_ip_port.split('@')
        auth = tuple(auth.split(":"))

    return conn, auth

