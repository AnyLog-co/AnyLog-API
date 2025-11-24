import aiohttp

NETWORK_ERRORS_GENERIC={
    1: "Informational",
    2: "Successful",
    3: "Redirection",
    4: "Client Error",
    5: "Server Error",
    7: "Developer Error"
}

NETWORK_ERRORS={
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
}


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

    try:
        error = int(error)
    except ValueError:
        pass  # Non-integer errors are handled as plain text

    if isinstance(error, int):
        if error in NETWORK_ERRORS:
            error_msg += f'(Network Error {error} - {NETWORK_ERRORS[error]})'
        elif int(str(error)[0]) in NETWORK_ERRORS_GENERIC:
            error_msg += f'(Network Error {error} - {NETWORK_ERRORS_GENERIC[int(str(error)[0])]})'
        else:
            error_msg += f'(Network Error: {error})'
    else:
        error_msg += f'(Error: {error})'

    raise Exception(error_msg)


async def __extract_results(cmd:str, response:aiohttp.ClientResponse, exception:bool=False)->str:
    output = None
    try:
        output= await response.json()
    except aiohttp.ContentTypeError:
        try:
            output= await response.text()
        except Exception as error:
            if exception:
                raise Exception(f'Failed to extract results for "{cmd}" (Error:{error})')
    return output


async def extract_get_results(command:str, response:aiohttp.ClientResponse, error:str=None):
    output = None
    if not response or response.status >= 400:
        __raise_rest_error(cmd_type='GET', cmd=command, error=error)
    elif not isinstance(response, bool):
        output= await __extract_results(cmd=command, response=response)

    return output


async def validate_put_post(cmd_type:str, command:str, response:aiohttp.ClientResponse, error:str=None)->bool:
    if not response or response.status >= 400:
        __raise_rest_error(cmd_type=cmd_type, cmd=command, error=error)
    return True
