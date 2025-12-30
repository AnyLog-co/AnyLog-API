# import requests
import asyncio
import httpx
from http import HTTPStatus
from typing import Optional

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

def __url_builder(conn:str, is_auth:bool=False):
    if not is_auth and not conn.startswith("http"):
        url = f"http://{conn}"
    elif is_auth and not conn.startswith("http"):
        url = f"https://{conn}"
    else:
        url = conn

    return url

def __resolve_network_error(status_code: int) -> str:
    # Exact match first
    if status_code in NETWORK_ERRORS:
        return NETWORK_ERRORS[status_code]

    # Generic class (2xx, 4xx, etc.)
    category = status_code // 100
    if category in NETWORK_ERRORS_GENERIC:
        return NETWORK_ERRORS_GENERIC[category]

    # Final fallback
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "Unknown Network Error"



async def rest_async_call(request_type:str, conn:str, headers:dict, payload=None, auth:tuple=(), timeout:float=30)->tuple[Optional[httpx.Response], Optional[str]]:
    url = __url_builder(conn)
    response: Optional[httpx.Response] = None
    err_msg: Optional[str] = None
    if not auth:
        auth = None
    try:
        async with httpx.AsyncClient(auth=auth, timeout=timeout) as client:
            response = await client.request(
                method=request_type.upper(),
                url=url,
                headers=headers,
                json=payload if isinstance(payload, dict) else None,
                content=payload if isinstance(payload, str) else None,
            )

        if response.is_error:
            status_code = response.status_code
            error_text = __resolve_network_error(status_code)

            err_msg = (
                f"Failed to execute {request_type.upper()} against {url} "
                f"(Network Error {status_code}: {error_text})"
            )

    except httpx.RequestError as exc:
        err_msg = f"Network error calling {url}: {exc}"

    except Exception as exc:
        err_msg = f"Unexpected error calling {url}: {exc}"

    return response, err_msg


def rest_call(request_type:str, conn:str, headers:dict, payload=None, auth:tuple=(), timeout:float=30)->tuple[Optional[httpx.Response], Optional[str]]:
    return asyncio.run(rest_async_call(request_type=request_type, conn=conn, headers=headers,payload=payload, auth=auth,
                                       timeout=timeout))

if __name__ == '__main__':
    response, err_msg = rest_call(request_type="GET", conn="23.239.12.151:32349", headers={"command": "get status", "User-Agent": "AnyLog/1.23"})
    if not err_msg and response:
        try:
            print(response.text)
        except Exception as error:
            print(error)
    else:
        print(err_msg)
