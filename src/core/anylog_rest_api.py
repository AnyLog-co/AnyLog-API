"""
anylog_rest_api.py
===================
This module is the CORE of the AnyLog-API package. Every other module in
`src/` (generic/, data/, blockchain/, ...) is built on top of the single
class defined here: `AnyLogRest`.

`AnyLogRest` is the only thing that actually speaks HTTP to an AnyLog/EdgeLake
node. Every "action" module elsewhere in the package (e.g. `generic/status.py`,
`generic/logs.py`) just builds a `headers` dict describing an AnyLog command
and hands it to one of `AnyLogRest`'s methods (`get`, `post`, `put`,
`get_via_post`) to actually run it. If you're adding a new command anywhere
else in the package, you should never need to touch this file — you just
need this file to keep working correctly, since a bug here breaks every
command in the package, not just one.

Design notes:
- Every REST verb has both an async version (`async_get`, `async_post`, ...)
  and a plain sync version (`get`, `post`, ...). The sync versions are thin
  wrappers that just call `asyncio.run(...)` on the async version, so all
  the real logic lives in one place (`__async_exec__`) instead of being
  duplicated — and possibly drifting out of sync — between async and sync
  code paths.
- AnyLog/EdgeLake GET-style commands (e.g. "get status") can also be sent
  as an HTTP POST, with the command placed in the JSON body instead of
  the URL/query string. `get_via_post` is what does this. Sending it as a
  POST keeps the command out of the URL, avoiding URL-length limits and
  keeping commands out of proxy/access logs.
- `exec_mode` lets a caller intercept a command before it's actually sent:
    - EXECUTE (default): run the command against the node as normal.
    - COMMAND: don't run anything — just return the AnyLog command string
      that *would* have been sent. Useful for debugging / dry runs.
    - HELP: don't run the command — instead print AnyLog's own `help`
      text for that command.
  This is checked once, centrally, in `__async_exec__`, so every method
  that routes through it (get/post/put/get_via_post) gets this behavior
  for free without repeating the check.
"""

import json
import asyncio
import httpx
import os

from src.core.support import ListCommands
from src.core.support import ExecMode
from src.core.support import load_json
from src.core.support import url_builder

ROOT_DIR = os.path.dirname(__file__)

# Human-readable text for HTTP status codes, used only to make error
# messages more useful (e.g. "404: Not Found" instead of just "404").
# Loaded once at import time. `load_json` (support.py) converts the JSON's
# string keys ("404") to int keys (404) — every lookup below uses int keys
# to match, since a str/int key mismatch means the lookup silently misses.
NETWORK_ERRORS = load_json(os.path.join(ROOT_DIR, "NETWORK_ERRORS.json"))
NETWORK_ERRORS_GENERIC = load_json(os.path.join(ROOT_DIR, "NETWORK_ERRORS_GENERIC.json"))


class AnyLogRest(ListCommands):
    """
    Low-level REST client for a single AnyLog/EdgeLake node.

    One instance = one node connection. Higher-level modules elsewhere in
    `src/` (generic, data, blockchain, ...) receive an `AnyLogRest` instance
    and use it to send commands; they never talk HTTP directly themselves.
    """

    def __init__(self, conn:str, auth:tuple=None, connection_timeout:float=30, read_timeout:float=30,
                 write_timeout:float=30, pool:float=5):
        """
        :logic:
            The code has both async and non-async code, that way a customer can execute commands in both formats.

            The non-async is a wrapper around the async command in order to limit / not have repeating the same code
            logic. this is also "safer" as it avoids many of the pitfalls of manual thread management and callback
            hell, making concurrent code more predictable and maintainable.

            In addition, utilizing POST over GET mitigates issues like CORs as it hides parameters in the body, so
            they're not exposed in the URL and are less likely to be logged in a way that leaks data.
            As such, AnyLog/EdgeLake's GET commands can be executed via POST with:
            - HEADERS: {"Content-Type": "application/json"}
            - DATA: {"command": [GET COMMAND], "AnyLog-Agent": "AnyLog/1.23", ["destination": "network"]}
        :args:
            conn:str - REST connection information (host:port, or a full URL)
            auth:tuple - (username, password) if the node requires basic auth. Passing
                auth also switches the generated URL to https — see `url_builder`.
            connection_timeout:float - seconds to wait for the TCP connection to establish
            read_timeout:float - seconds to wait for response data once connected
            write_timeout:float - seconds to wait while sending request data
            pool:float - seconds to wait for a free connection slot in httpx's connection pool
        :params:
            self.conn:str - generated URL for connecting to AnyLog/EdgeLake
            self.auth:tuple - Username/password authentication if provided
            self.timeout - the full REST request timeout policy (httpx.Timeout)
            self.exec_mode:ExecMode - default execution mode for commands run through this
                connection (see `update_exec_mode` below); starts as EXECUTE.
        """
        self.conn = url_builder(conn=conn, is_auth=bool(auth))
        self.auth = auth
        self.exec_mode = ExecMode.EXECUTE

        try:
            self.timeout = httpx.Timeout(
                connect=connection_timeout,
                read=read_timeout,
                write=write_timeout,
                pool=pool
            )
        except Exception as error:
            # httpx.Timeout() raises plain ValueError/TypeError on bad args
            # (not an httpx-specific exception type), so we catch broadly
            # here rather than a narrow httpx exception class.
            raise Exception(f"Failed to define connection timeout information (Error: {error})")

    def update_exec_mode(self, exec_mode:str):
        """
        Change how commands run through this connection behave by default.
        :args:
            exec_mode:str - one of:
                - "execute" (default): actually run the command
                - "command": don't run it, just return the AnyLog command string
                - "help": don't run it, print AnyLog's help text for it instead
        """
        self.exec_mode = ExecMode.EXECUTE
        if exec_mode.lower() == "command":
            self.exec_mode = ExecMode.COMMAND
        elif exec_mode.lower() == "help":
            self.exec_mode = ExecMode.HELP
        elif exec_mode.lower() == "info":
            self.exec_mode = ExecMode.INFO

    async def __async_exec__(self, cmd_type:str, headers:dict, payload=None, exec_mode=ExecMode.EXECUTE):
        """
        Single choke point every request (GET/POST/PUT, sync or async)
        eventually routes through. This is where `exec_mode` is actually
        honored and where the real httpx call happens — new "does this
        request actually get sent" logic belongs here, not duplicated
        per-method below.
        :args:
            cmd_type:str - HTTP method to use ("GET", "POST", or "PUT")
            headers:dict - REST headers; must include "command" (the AnyLog command string)
            payload - content to send in the request body (dict -> sent as JSON,
                str -> sent as raw content, None -> no body)
        :params:
            status_code_str - human-readable text for a failing HTTP status code
            response - the raw httpx.Response (only reached when exec_mode == EXECUTE)
        :exception:
            httpx.NetworkError - node responded with a non-2xx status
            httpx.TimeoutException - request timed out
            Exception - anything else that goes wrong making the request
        :return:
            - exec_mode == COMMAND: the AnyLog command string (nothing is sent)
            - exec_mode == HELP: None (help text is printed, not returned)
            - exec_mode == EXECUTE: the raw httpx.Response
            - exec_mode == INFO: print python function name + description
        """
        command = headers["command"]
        if exec_mode == ExecMode.COMMAND:
            return command
        elif exec_mode == ExecMode.HELP:
            await self.async_help(command)
            return None

        # exec_mode == EXECUTE from here down: actually send the request.
        try:
            async with httpx.AsyncClient(auth=self.auth, timeout=self.timeout) as client:
                response = await client.request(method=cmd_type.upper(), url=self.conn, headers=headers,
                                                json=payload if isinstance(payload, dict) else None,
                                                content=payload if isinstance(payload, str) else None)

                status_code = int(response.status_code)
                if response is not None and not 200 <= status_code < 300:
                    # NETWORK_ERRORS / NETWORK_ERRORS_GENERIC are both keyed
                    # by int (see load_json in support.py) — look up with
                    # int keys here too, or the lookup silently misses and
                    # status_code_str ends up unset/None.
                    if status_code in NETWORK_ERRORS:
                        status_code_str = NETWORK_ERRORS[status_code]
                    elif int(str(status_code)[0]) in NETWORK_ERRORS_GENERIC:
                        # Fall back to the coarse "4xx / 5xx" category when
                        # the exact status code isn't in NETWORK_ERRORS.
                        status_code_str = NETWORK_ERRORS_GENERIC[int(str(status_code)[0])]
                    else:
                        status_code_str = "Unknown Error"
                    raise httpx.NetworkError(f"Failed to execute {cmd_type.upper()} against {self.conn} (Network Error {status_code}: {status_code_str})")
        except httpx.TimeoutException as error:
            raise httpx.TimeoutException(f"Request timed out against {self.conn} (Error: {error})")
        except Exception as error:
            raise Exception(f"Failed to execute {cmd_type.upper()} against {self.conn} (Error: {error})")

        return response

    async def async_get(self, headers:dict, exec_mode=ExecMode.EXECUTE):
        """
        Generic GET request against AnyLog/EdgeLake.
        :args:
            headers:dict - REST headers; must include "command"
        :return:
            parsed JSON body when the response is JSON; otherwise the raw
            value from `__async_exec__` (COMMAND string / HELP's None) or
            the response's raw text as a last-resort fallback
        """
        response = await self.__async_exec__(cmd_type="GET", headers=headers, exec_mode=exec_mode)

        try:
            return response.json()
        except AttributeError:
            # response isn't an httpx.Response (e.g. COMMAND mode returned a
            # plain string, or HELP mode returned None) — pass it through as-is.
            return response
        except Exception:
            # Response wasn't valid JSON — fall back to raw text.
            return response.text

    def get(self, headers:dict, exec_mode=ExecMode.EXECUTE):
        """Sync wrapper around `async_get` — see that method for the actual logic."""
        return asyncio.run(self.async_get(headers=headers, exec_mode=exec_mode))

    async def async_post(self, headers:dict, payload=None, exec_mode=ExecMode.EXECUTE):
        """
        Generic POST request against AnyLog/EdgeLake.
        :args:
            headers:dict - REST headers; must include "command"
            payload - content to publish to AnyLog/EdgeLake
        :return:
            raw httpx.Response (or the COMMAND string / HELP's None, depending on exec_mode)
        """
        # AnyLog expects the client identity under the "AnyLog-Agent" header.
        # Normalize a caller-supplied "User-Agent" into that, and default it
        # if the caller didn't set either.
        if "User-Agent" in headers:
            headers["AnyLog-Agent"] = headers.pop("User-Agent")
        elif headers.get("AnyLog-Agent") is None:
            headers["AnyLog-Agent"] = "AnyLog/1.23"

        return await self.__async_exec__(cmd_type="POST", headers=headers, payload=payload, exec_mode=exec_mode)

    def post(self, headers:dict, payload=None, exec_mode=ExecMode.EXECUTE):
        """Sync wrapper around `async_post` — see that method for the actual logic."""
        return asyncio.run(self.async_post(headers=headers, payload=payload, exec_mode=exec_mode))

    async def async_get_via_post(self, headers:dict, exec_mode=ExecMode.EXECUTE):
        """
        Execute a GET-style AnyLog command by sending it as an HTTP POST
        instead of a real GET. See the `:logic:` note in `__init__` for why
        (keeps the command out of the URL / access logs). The GET command's
        headers are serialized as JSON into the POST body.
        :args:
            headers:dict - the GET command's headers (same shape `async_get` takes)
        :return:
            parsed JSON body, or raw text if the response isn't JSON
        """
        if "User-Agent" in headers:
            headers["AnyLog-Agent"] = headers.pop("User-Agent")
        else:
            headers["AnyLog-Agent"] = "AnyLog/1.23"
        payload = json.dumps(headers)
        request_headers = {
            "Content-Type": "application/json"
        }
        response = await self.__async_exec__(cmd_type="POST", headers=request_headers, payload=payload, exec_mode=exec_mode)

        try:
            return response.json()
        except AttributeError:
            return response
        except Exception:
            return response.text

    def get_via_post(self, headers:dict, exec_mode=ExecMode.EXECUTE):
        """Sync wrapper around `async_get_via_post` — see that method for the actual logic."""
        return asyncio.run(self.async_get_via_post(headers=headers, exec_mode=exec_mode))

    async def async_put(self, headers:dict, payload=None, exec_mode=ExecMode.EXECUTE):
        """
        Generic PUT request against AnyLog/EdgeLake.
        :args:
            headers:dict - REST headers; must include "command"
            payload - content to publish to AnyLog/EdgeLake
        :return:
            raw httpx.Response (or the COMMAND string / HELP's None, depending on exec_mode)
        """
        return await self.__async_exec__(cmd_type="PUT", headers=headers, payload=payload, exec_mode=exec_mode)

    def put(self, headers:dict, payload=None, exec_mode=ExecMode.EXECUTE):
        """Sync wrapper around `async_put` — see that method for the actual logic."""
        return asyncio.run(self.async_put(headers=headers, payload=payload, exec_mode=exec_mode))

    async def async_help(self, command:str=None, exec_mode=ExecMode.EXECUTE):
        """
        Print AnyLog's own help text: either the full command list (no
        `command` given) or help for one specific command.
        Note this is the one method that prints instead of returning a
        value — call `async_get`/`get` yourself with a "help ..." command
        if you need the text back as a value instead of printed to stdout.
        :args:
            command:str - command to get information for (None = list all commands)
        """
        headers = {
            "command": f"help {command}" if command else "help",
            "User-Agent": "AnyLog/1.23"
        }

        output = await self.async_get(headers=headers, exec_mode=exec_mode)
        print(output)

    def help(self, command:str=None, exec_mode=ExecMode.EXECUTE):
        """Sync wrapper around `async_help` — see that method for the actual logic."""
        asyncio.run(self.async_help(command=command, exec_mode=exec_mode))
