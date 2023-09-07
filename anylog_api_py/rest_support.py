# Network errors based on: https://github.com/for-GET/know-your-http-well/blob/master/json/status-codes.json

import argparse
import re
import requests


NETWORK_ERRORS_GENERIC = {
    1: "Informational",
    2: "Successful",
    3: "Redirection",
    4: "Client Error",
    5: "Server Error",
    7: "Developer Error"
}
NETWORK_ERRORS = {
    100: "Continue",
    101: "Switching Protocols",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    307: "Temporary Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Payload Too Large",
    414: "URI Too Long",
    415: "Unsupported Media Type",
    416: "Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",
    426: "Upgrade Required",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Time-out",
    505: "HTTP Version Not Supported",
    102: "Processing",
    207: "Multi-Status",
    226: "IM Used",
    308: "Permanent Redirect",
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    451: "Unavailable For Legal Reasons",
    506: "Variant Also Negotiates",
    507: "Insufficient Storage",
    511: "Network Authentication Required"
}


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


def print_rest_error(call_type:str, cmd:str, error:str):
    """
    Print Error message
    :args:
        error_type:str - Error Type
        cmd:str - command that failed
        error:str - error message
    :params:
        error_msg:str - generated error message
    :print:
        error message
    """
    error_msg = f'Failed to execute {call_type} for "{cmd}" '

    try:
        error = int(error)
    except:
        pass
    if isinstance(error, int):
        if error in NETWORK_ERRORS:
            error_msg += f'(Network Error {error} - {NETWORK_ERRORS[error]})'
        elif int(str(error)[0]) in NETWORK_ERRORS_GENERIC:
            error_msg += f'(Network Error {error} - {NETWORK_ERRORS_GENERIC[int(str(error)[0])]})'
        else:
            error_msg += f'(Network Error: {error})'
    else:
        error_msg += f'(Error: {error})'

    print(error_msg)


def extract_results(cmd:str, r:requests.get, exception:bool=False)->str:
    """
    Given the results from a GET request, extract the results as JSON, then text if JSON fails
    :args:
        cmd:str - original command executed
        r:requests.get - (raw) results from GET request
        exception:bool - whether to print exceptions
    :params:
        output:str - result from GET request
    :return:
        if success returns result as either JSON or text, if fails returns None
    """
    output = None
    try:
        output = r.json()
    except Exception as error:
        try:
            output = r.text
        except Exception as error:
            if exception is True:
                print(f'Failed to extract results for "{cmd}" (Error: {error})')

    return output


def generate_connection_command(conn_type:str, internal_ip:str, internal_port:int, external_ip:str=None,
                                external_port:int=None, bind:bool=True, threads:int=3, rest_timeout:int=30)->str:
    """
    Generate connection to network command
    :args:
        conn_type:str - connection type (TCP, REST, broker)
        internal_ip:str - internal/local  ip
        internal_port  - internal/local ip
        external_ip:str - external ip
        external_port:str - external port
        bind:bool - whether to bind or not
        threads:int - number of threads
        rest_timeout:bool - REST timeout
    :params:
        command:str - generatedd command
    :return:
        command
    """
    if conn_type.upper() == 'TCP':
        command = 'run tcp server where'
    elif conn_type.upper() == 'REST':
        command = 'run rest server where '
    elif conn_type.lower() == 'broker':
        command = 'run message broker where '

    if external_ip is not None:
        command += f'external_ip={external_ip} and '
    else:
        command += f'external_ip={internal_ip} and '
    if external_port is not None:
        command += f'external_ip={external_port} and '
    else:
        command += f'external_ip={internal_port} and '
    command += f'internal_ip={internal_ip} and internal_port={internal_port} and '

    if bind is True:
        command += ' bind=true and '
    else:
        command += ' bind=false and '
    command += f'threads={threads}'

    if conn_type.upper() == 'REST':
        command += f' timeout={rest_timeout}'

    return command
