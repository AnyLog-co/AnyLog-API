"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import ast
import re
import requests

# Network errors based on: https://github.com/for-GET/know-your-http-well/blob/master/json/status-codes.json
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

def __extract_embedded_json(error):
    error_output = None

    try:
        # Try literal eval (e.g. if it's a tuple)
        error_output = ast.literal_eval(error)
    except Exception:
        error_output = error

    # Convert tuple to string if needed
    if isinstance(error_output, tuple):
        error_output = str(error_output)

    # Step: extract JSON from within a messy string
    try:
        match = re.search(r'\{.*?\}', error_output)
        if match:
            json_str = match.group(0)
            error_output = ast.literal_eval(json_str.strip('"').replace("\\\\", "\\") .replace("\\'", "'"))
    except Exception as e:
        raise ValueError(f"Failed to extract valid JSON: {e}")

    return error_output


def __raise_rest_error(cmd_type:str, cmd:str, error:str):
    """
    Print Error message
    :args:
        error_type:str - Error Type
        cmd:str - command that failed
        error:str - error message
    :global:
        NETWORK_ERRORS:dict - based on initial error code value print error message
        NETWORK_ERRORS_GENERIC:dict - based on initial error code value print error message
    :params:
        error_msg:str - generated error message
    :raise:
        error message
    """
    error_msg = f'Failed to execute {cmd_type} for "{cmd}" '
    error = __extract_embedded_json(error)

    if isinstance(error, int):
        if error in NETWORK_ERRORS:
            error_msg += f'(Network Error {error} - {NETWORK_ERRORS[error]})'
        elif int(str(error)[0]) in NETWORK_ERRORS_GENERIC:
            error_msg += f'(Network Error {error} - {NETWORK_ERRORS_GENERIC[int(str(error)[0])]})'
        else:
            error_msg += f'(Network Error: {error})'
    else:
        error_msg += f"(Error: {error['err_text']})"

    raise requests.RequestException(error_msg)


def __extract_results(cmd:str, r:requests.get, exception:bool=False)->str:
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
    except requests.JSONDecodeError:
        try:
            output = r.text
        except Exception as error:
            if exception is True:
                raise requests.JSONDecodeError(f'Failed to extract results for "{cmd}" (Error: {error})')

    return output


def extract_get_results(command:str, response:requests.get, error:str=None):
    """
    execute / extract results for GET request
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        headers:dict - REST headers
        exception:bool - whether to print exception
    :params:
        output - results from GET request
    :return:
        output
    """
    output = None
    if response is False:
        __raise_rest_error(cmd_type='GET', cmd=command, error=error)
    elif not isinstance(response, bool):
        output = __extract_results(cmd=command, r=response)

    return output


def validate_put_post(cmd_type:str, command:str, response, error:str=None)->bool:
    status = True
    if response is False:
        __raise_rest_error(cmd_type=cmd_type, cmd=command, error=error)

    return status