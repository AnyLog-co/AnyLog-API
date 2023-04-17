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


def print_rest_error(call_type:str, cmd:str, error):
    """
    Print Error message
    :args:
        error_type:str - Error Type
        cmd:str - command that failed
        error - error message
    :global:
        NETWORK_ERRORS_GENERIC:dict - generic error message for a given error code
        NETWORK_ERRORS:dict  - specific error message for a given error code
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


class AnyLogConnector:
    def __init__(self, conn:str, auth:tuple=None, timeout:int=30, exception:bool=False):
        """
        Connection to AnyLog node
        :args:
            conn:Str - REST connection information
            auth:tuple - authentication information
            timeout:int - REST timeout
            exception:bool - whether to print exception
        """
        self.conn = conn
        self.auth = auth
        self.timeout = timeout
        self.exception = exception

    def get(self, headers:dict):
        """
        Execute GET command
        :args:
            headers:dict - REST header information
        :params:
            r:requests.request - REST request results
        :return:
            r
        """
        try:
            r = requests.get(url=f'http:{self.conn}', auth=self.auth, timeout=self.timeout, headers=headers)
        except Exception as error:
            r = None
            if self.exception is True:
                print_rest_error(call_type="GET", cmd=headers["command"], error=error)
        else:
            if int(r.status_code) != 200:
                if self.exception is True:
                    print_rest_error(call_type="GET", cmd=headers["command"], error=r.status_code)
                r = None

        return r

    def post(self, headers:dict):
        """
        Execute POST command
        :args:
            headers:dict - REST header information
        :params:
            r:requests.request - REST request results
        :return:
            r
        """
        try:
            r = requests.post(url=f'http:{self.conn}', auth=self.auth, timeout=self.timeout, headers=headers)
        except Exception as error:
            r = None
            if self.exception is True:
                print_rest_error(call_type="POST", cmd=headers["command"], error=error)
        else:
            if int(r.status_code) != 200:
                if self.exception is True:
                    print_rest_error(call_type="POST", cmd=headers["command"], error=r.status_code)
                r = None

        return r

    def put(self, headers:dict):
        """
        Execute PUT command
        :args:
            headers:dict - REST header information
        :params:
            r:requests.request - REST request results
        :return:
            r
        """
        try:
            r = requests.put(url=f'http:{self.conn}', auth=self.auth, timeout=self.timeout, headers=headers)
        except Exception as error:
            r = None
            if self.exception is True:
                print_rest_error(call_type="PUT", cmd=headers["command"], error=error)
        else:
            if int(r.status_code) != 200:
                if self.exception is True:
                    print_rest_error(call_type="PUT", cmd=headers["command"], error=r.status_code)
                r = None

        return r