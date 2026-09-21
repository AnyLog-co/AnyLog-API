import json
import asyncio
import httpx
import os

from src.core.support import ListCommands
from src.core.support import ExecMode
from src.core.support import load_json
from src.core.support import url_builder

ROOT_DIR = os.path.dirname(__file__)

NETWORK_ERRORS = load_json(os.path.join(ROOT_DIR, "NETWORK_ERRORS.json"))
NETWORK_ERRORS_GENERIC = load_json(os.path.join(ROOT_DIR, "NETWORK_ERRORS_GENERIC.json"))


class AnyLogRest(ListCommands):
    def __init__(self, conn:str, auth:tuple=None, connection_timeout:float=30, read_timeout:float=30,
                 write_timeout:float=30, pool:float=5):
        """
        AnyLog REST class is Anylog/EdgeLake specific tool to communicate with AnyLog/EdgeLake API using either
        asynchronous or synchronous requests via httpx.
        :args:
            conn:str - REST connection information
            auth:tuple - authentication
            connection_timeout:float - TCP connection establishment
            read_timeout:float - Waiting for response data
            write_timeout:float - Sending request data
        """
        self.conn = url_builder(conn=conn, is_auth=bool(auth))
        self.auth = auth
        try:
            self.timeout = httpx.Timeout(
                connect=connection_timeout,
                read=read_timeout,
                write=write_timeout,
                pool=pool
            )
        except (httpx.TimeoutException or Exception) as error:
            raise Exception(f"Failed to define connection timeout information (Error: {error})")

        # self.exec_mode = ExecMode.EXECUTE


    async def __async_exec__(self, cmd_type:str, headers:dict, payload=None, exec_mode=ExecMode.EXECUTE):
        """
        Execute request against AnyLog / EdgeLake instance
        :args:
            cmd_type:str - command type (GET, PUT and POST)
            headers:dict - RESt headers
            payload - content to publish to AnyLog/EdgeLake
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """
        command = headers["command"]
        if exec_mode == ExecMode.COMMAND:
            return command
        elif exec_mode == ExecMode.HELP:
            await self.async_help(command)
            return None
        else:
            try:
                async with  httpx.AsyncClient(auth=self.auth, timeout=self.timeout) as client:
                    response = await client.request(method=cmd_type.upper(), url=self.conn, headers=headers,
                                                    json=payload if isinstance(payload, dict) else None,
                                                    content=payload if isinstance(payload, str) else None)

                    status_code = int(response.status_code)
                    if response and not 200 <= int(response.status_code) < 300:
                        if NETWORK_ERRORS.get(status_code):
                            status_code_str = NETWORK_ERRORS.get(str(status_code))
                        elif NETWORK_ERRORS_GENERIC.get(status_code):
                            status_code_str = NETWORK_ERRORS_GENERIC.get(str(status_code)[0])
                        raise httpx.NetworkError(f"Failed to execute {cmd_type.upper()} against {self.conn} (Network Error {status_code}: {status_code_str})")
            except httpx.TimeoutException as error:
                raise httpx.TimeoutException(f"Request timed out against {self.conn} (Error: {error})")

            except Exception as error:
                raise Exception(f"Failed to execute {cmd_type.upper()} against {self.conn} (Error: {error})")

            return response


    async def async_get(self, headers:dict, exec_mode=ExecMode.EXECUTE):
        """
        Generic method for GET requests against AnyLog/EdgeLake
        :args:
            headers:dict - REST headers
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            actual content from response
        """
        response = await self.__async_exec__(cmd_type="GET", headers=headers, exec_mode=exec_mode)

        try:
            return response.json()
        except AttributeError:
            return response
        except Exception:
            return response.text


    def get(self, headers:dict, exec_mode=ExecMode.EXECUTE):
        """
        Generic method for GET requests against AnyLog/EdgeLake
        :args:
            headers:dict - RESt headers
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """
        return asyncio.run(self.async_get(headers=headers, exec_mode=exec_mode))

    async def async_post(self, headers:dict, payload=None, exec_mode=ExecMode.EXECUTE):
        """
        Generic method for POST requests against AnyLog/EdgeLake
        :args:
            headers:dict - RESt headers
            payload - content to publish to AnyLog/EdgeLake
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """
        if "User-Agent" in headers:
            headers["AnyLog-Agent"] = headers.pop("User-Agent")
        elif headers.get("AnyLog-Agent") is None:
            headers["AnyLog-Agent"] = "AnyLog/1.23"

        return await self.__async_exec__(cmd_type="POST", headers=headers, payload=payload, exec_mode=exec_mode)


    def post(self, headers:dict, payload=None, exec_mode=ExecMode.EXECUTE):
        """
        Generic method for POST requests against AnyLog/EdgeLake
        :args:
            headers:dict - RESt headers
            payload - content to publish to AnyLog/EdgeLake
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """
        return asyncio.run(self.async_post(headers=headers, payload=payload, exec_mode=exec_mode))


    async def async_get_via_post(self, headers:dict, exec_mode=ExecMode.EXECUTE):
        """
        Generic method for executing GET requests via POST
        :args:
            headers:dict - GET command REST headers
        :params:
            payload:str - serialized GET headers
            request_headers:dict - headers for REST
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
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
        """
        Generic method for executing GET requests via POST
        :args:
            headers:dict - GET command REST headers
        :params:
            payload:str - serialized GET headers
            request_headers:dict - headers for REST
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """
        return asyncio.run(self.async_get_via_post(headers=headers, exec_mode=exec_mode))


    async def async_put(self, headers:dict, payload=None, exec_mode=ExecMode.EXECUTE):
        """
        Generic method for PUT requests against AnyLog/EdgeLake
        :args:
            headers:dict - RESt headers
            payload - content to publish to AnyLog/EdgeLake
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """
        return await self.__async_exec__(cmd_type="PUT", headers=headers, payload=payload, exec_mode=exec_mode)


    def put(self, headers:dict, payload=None, exec_mode=ExecMode.EXECUTE):
        """
        Generic method for PUT requests against AnyLog/EdgeLake
        :args:
            headers:dict - REST headers
            payload - content to publish to AnyLog/EdgeLake
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """
        return asyncio.run(self.async_put(headers=headers, payload=payload, exec_mode=exec_mode))


    async def async_help(self, command:str=None, exec_mode=ExecMode.EXECUTE):
        """
        get list of commands  or information about a command
        :args:
            command:str - command to get information for
        :params;
            headers:dict - REST headers
        :return:
            this is the only method that doesn't return a
        """
        headers = {
            "command": f"help {command}" if command else "help",
            "User-Agent": "AnyLog/1.23"
        }

        output = await self.async_get(headers=headers, exec_mode=exec_mode)
        print(output)

    def help(self, command:str=None, exec_mode=ExecMode.EXECUTE):
        """
        get list of commands  or information about a command
        :args:
            command:str - command to get information for
        :params;
            headers:dict - REST headers
        :return:
            this is the only method that doesn't return a
        """
        asyncio.run(self.async_help(command=command, exec_mode=exec_mode))


    def update_exec_mode(self, exec_mode:str):
        """
        Update execution mode for a given command
        :args:
            exec_mode:
            - execute (default)
            - command: returns command
            - help: prints help information for the command
            - info: function information
        """
        self.exec_mode = ExecMode.EXECUTE
        if exec_mode.lower() == "command":
            self.exec_mode = ExecMode.COMMAND
        elif exec_mode.lower() == "help":
            self.exec_mode = ExecMode.HELP
        # elif exec_mode.lower() == "info":
        #     self.exec_mode =ExecMode.INFO