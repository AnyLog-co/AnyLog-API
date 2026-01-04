import asyncio
import httpx
import os
import anylog_api.support as support

from pprint import pprint

ROOT_DIR = os.path.dirname(__file__)
NETWORK_ERRORS = support.load_json(os.path.join(ROOT_DIR, "NETWORK_ERRORS.json"))
NETWORK_ERRORS_GENERIC = support.load_json(os.path.join(ROOT_DIR, "NETWORK_ERRORS_GENERIC.json"))

class AnyLogRest:
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
        self.conn = support.url_builder(conn=conn, is_auth=bool(auth))
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


    def list_commands(self):
        """
        provide docstring / help for functions
        """
        return {
            name: getattr(self, name).__doc__
            for name in dir(self)
            if not name.startswith("_") and callable(getattr(self, name))
        }

    def connect(self):
        status = Status()


    async def __async_exec__(self, cmd_type:str, headers:dict, payload=None):
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
                    raise httpx.NetworkError(f"Failed to execute {cmd_type.upper()} against {conn} (Network Error {status_code}: {status_code_str})")
        except httpx.TimeoutException as error:
            raise httpx.TimeoutException(f"Request timed out against {self.conn} (Error: {error})")

        except Exception as error:
            raise Exception(f"Failed to execute {cmd_type.upper()} against {self.conn} (Error: {error})")

        return response


    def __sync_exec__(self, cmd_type:str, headers:dict, payload=None):
        """
        Execute request against AnyLog / EdgeLake instance - calls async process
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

        return asyncio.run(self.__async_exec__(cmd_type=cmd_type, headers=headers, payload=payload))

    async def async_get(self, headers:dict):
        """
        Execute request against AnyLog / EdgeLake instance - calls async process
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
        response = await self.__async_exec__(cmd_type="GET", headers=headers)

        try:
            return response.json()
        except Exception:
            return response.text


    def get(self, headers:dict):
        """
        Execute request against AnyLog / EdgeLake instance - calls async process
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
        return asyncio.run(self.async_get(headers=headers))

    async def async_post(self, headers:dict, payload=None):
        """
        Execute request against AnyLog / EdgeLake instance - calls async process
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
        return await self.__async_exec__(cmd_type="POST", headers=headers, payload=payload)


    def post(self, headers:dict, payload=None):
        """
        Execute request against AnyLog / EdgeLake instance - calls async process
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
        return self.__sync_exec__(cmd_type="POST", headers=headers, payload=payload)


    async def async_put(self, headers:dict, payload=None):
        """
        Execute request against AnyLog / EdgeLake instance - calls async process
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
        return await self.__async_exec__(cmd_type="PUT", headers=headers, payload=payload)


    def put(self, headers:dict, payload=None):
        """
        Execute request against AnyLog / EdgeLake instance - calls async process
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
        return self.__sync_exec__(cmd_type="PUT", headers=headers)


    async def async_help(self, command:str=None):
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

        output = await self.async_get(headers=headers)
        print(output)

    def help(self, command:str=None):
        """
        get list of commands  or information about a command
        :args:
            command:str - command to get information for
        :params;
            headers:dict - REST headers
        :return:
            this is the only method that doesn't return a
        """
        asyncio.run(self.async_help(command=command))


