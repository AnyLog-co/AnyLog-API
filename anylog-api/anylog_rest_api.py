import asyncio
import httpx
import os
import support

from abc import ABC

ROOT_DIR = os.path.dirname(__file__)
NETWORK_ERRORS = support.load_json(os.path.join(ROOT_DIR, "NETWORK_ERRORS.json"))
NETWORK_ERRORS_GENERIC = support.load_json(os.path.join(ROOT_DIR, "NETWORK_ERRORS_GENERIC.json"))

class AnyLogRest(ABC):
    def __init__(self, conn:str=None, auth:tuple=None, connection_timeout:float=30, read_timeout:float=30, write_timeout:float=30):
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
        self.connection_timeout = connection_timeout
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout


    def list_commands(self):
        """
        provide docstring / help for functions
        """
        return {
            name: getattr(self, name).__doc__
            for name in dir(self)
            if not name.startswith("_") and callable(getattr(self, name))
        }


    async def __async_exec__(self, cmd_type:str, headers:dict, payload=None, conn:str=None, auth:tuple=None,
                             connection_timeout:float=None, read_timeout:float=None, write_timeout:float=None):
        """
        Execute request against AnyLog / EdgeLake instance
        :args:
            cmd_type:str - command type (GET, PUT and POST)
            headers:dict - RESt headers
            payload - content to publish to AnyLog/EdgeLake
        :overwrite options:
        Option to overwrite default configs
            conn:str - REST connection information
            auth:tuple - authentication
            connection_timeout:float - TCP connection establishment
            read_timeout:float - Waiting for response data
            write_timeout:float - Sending request data
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """
        status_code_str = "UNKNOWN"
        auth = auth if auth else self.auth
        conn = support.url_builder(conn=conn, is_auth=bool(auth)) if conn else self.conn
        connection_timeout = connection_timeout if connection_timeout else self.connection_timeout
        read_timeout = read_timeout if read_timeout else self.read_timeout
        write_timeout = write_timeout if write_timeout else self.write_timeout

        try:
            timeout = httpx.Timeout(
                connect=connection_timeout,
                read=read_timeout,
                write=write_timeout
            )
            async with httpx.AsyncClient(auth=auth, timeout=timeout) as client:
                response = await client.request(method=cmd_type.upper(), url=conn, headers=headers,
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
            raise httpx.TimeoutException(f"Request timed out against {conn} (Error: {error})")

        except Exception as error:
            raise Exception(f"Failed to execute {cmd_type.upper()} against {conn} (Error: {error})")

        return response


    def __sync_exec__(self, cmd_type:str, headers:dict, payload=None, conn:str=None, auth:tuple=None,
                  connection_timeout:float=None, read_timeout:float=None, write_timeout:float=None):
        """
        Execute request against AnyLog / EdgeLake instance - calls async process
        :args:
            cmd_type:str - command type (GET, PUT and POST)
            headers:dict - RESt headers
            payload - content to publish to AnyLog/EdgeLake
        :overwrite options:
        Option to overwrite default configs
            conn:str - REST connection information
            auth:tuple - authentication
            connection_timeout:float - TCP connection establishment
            read_timeout:float - Waiting for response data
            write_timeout:float - Sending request data
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """

        return asyncio.run(self.__a__sync_exec____(cmd_type=cmd_type, headers=headers, payload=payload, conn=conn, auth=auth,
                         connection_timeout=connection_timeout, read_timeout=read_timeout, write_timeout=write_timeout))

    async def async_get(self, headers:dict, conn:str=None, auth:tuple=None, connection_timeout:float=None,
                        read_timeout:float=None, write_timeout:float=None):
        """
        Execute request against AnyLog / EdgeLake instance - calls async process
        :args:
            cmd_type:str - command type (GET, PUT and POST)
            headers:dict - RESt headers
        :overwrite options:
        Option to overwrite default configs
            conn:str - REST connection information
            auth:tuple - authentication
            connection_timeout:float - TCP connection establishment
            read_timeout:float - Waiting for response data
            write_timeout:float - Sending request data
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """
        return await self.__a__sync_exec____(cmd_type="GET", headers=headers, conn=conn, auth=auth,
                         connection_timeout=connection_timeout, read_timeout=read_timeout, write_timeout=write_timeout)

    def get(self, headers:dict, conn:str=None, auth:tuple=None, connection_timeout:float=None, read_timeout:float=None,
            write_timeout:float=None):
        """
        Execute request against AnyLog / EdgeLake instance - calls async process
        :args:
            cmd_type:str - command type (GET, PUT and POST)
            headers:dict - RESt headers
        :overwrite options:
        Option to overwrite default configs
            conn:str - REST connection information
            auth:tuple - authentication
            connection_timeout:float - TCP connection establishment
            read_timeout:float - Waiting for response data
            write_timeout:float - Sending request data
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """

        return self.__sync_exec__(cmd_type="GET", headers=headers, conn=conn, auth=auth,
                              connection_timeout=connection_timeout, read_timeout=read_timeout,
                              write_timeout=write_timeout)

    async def async_post(self, headers:dict, payload=None, conn:str=None, auth:tuple=None, connection_timeout:float=None,
                         read_timeout:float=None, write_timeout:float=None):
        """
        Execute request against AnyLog / EdgeLake instance - calls async process
        :args:
            cmd_type:str - command type (GET, PUT and POST)
            headers:dict - RESt headers
            payload - content to publish to AnyLog/EdgeLake
        :overwrite options:
        Option to overwrite default configs
            conn:str - REST connection information
            auth:tuple - authentication
            connection_timeout:float - TCP connection establishment
            read_timeout:float - Waiting for response data
            write_timeout:float - Sending request data
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """
        return await self.__a__sync_exec____(cmd_type="POST", headers=headers, payload=payload, conn=conn, auth=auth,
                                     connection_timeout=connection_timeout, read_timeout=read_timeout,
                                     write_timeout=write_timeout)


    def post(self, headers:dict, payload=None, conn:str=None, auth:tuple=None, connection_timeout:float=None,
             read_timeout:float=None, write_timeout:float=None):
        """
        Execute request against AnyLog / EdgeLake instance - calls async process
        :args:
            cmd_type:str - command type (GET, PUT and POST)
            headers:dict - RESt headers
            payload - content to publish to AnyLog/EdgeLake
        :overwrite options:
        Option to overwrite default configs
            conn:str - REST connection information
            auth:tuple - authentication
            connection_timeout:float - TCP connection establishment
            read_timeout:float - Waiting for response data
            write_timeout:float - Sending request data
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """
        return self.__sync_exec__(cmd_type="POST", headers=headers, payload=payload, conn=conn, auth=auth,
                              connection_timeout=connection_timeout, read_timeout=read_timeout,
                              write_timeout=write_timeout)


    async def async_put(self, headers:dict, payload=None, conn:str=None, auth:tuple=None, connection_timeout:float=None,
                        read_timeout:float=None, write_timeout:float=None):
        """
        Execute request against AnyLog / EdgeLake instance - calls async process
        :args:
            cmd_type:str - command type (GET, PUT and POST)
            headers:dict - RESt headers
            payload - content to publish to AnyLog/EdgeLake
        :overwrite options:
        Option to overwrite default configs
            conn:str - REST connection information
            auth:tuple - authentication
            connection_timeout:float - TCP connection establishment
            read_timeout:float - Waiting for response data
            write_timeout:float - Sending request data
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """
        return await self.__a__sync_exec____(cmd_type="PUT", headers=headers, payload=payload, conn=conn, auth=auth,
                                     connection_timeout=connection_timeout, read_timeout=read_timeout,
                                     write_timeout=write_timeout)


    def put(self, headers:dict, payload=None, conn:str=None, auth:tuple=None, connection_timeout:float=None,
            read_timeout:float=None, write_timeout:float=None):
        """
        Execute request against AnyLog / EdgeLake instance - calls async process
        :args:
            cmd_type:str - command type (GET, PUT and POST)
            headers:dict - RESt headers
            payload - content to publish to AnyLog/EdgeLake
        :overwrite options:
        Option to overwrite default configs
            conn:str - REST connection information
            auth:tuple - authentication
            connection_timeout:float - TCP connection establishment
            read_timeout:float - Waiting for response data
            write_timeout:float - Sending request data
        :params:
            status_code_str - error message if fails
            timeout:httpx.timeout - REST timeout
            response - request response
        :exception:
            Network Error || Exception if execution fails
        :return:
            raw response
        """
        return self.__sync_exec__(cmd_type="PUT", headers=headers, payload=payload, conn=conn, auth=auth,
                              connection_timeout=connection_timeout, read_timeout=read_timeout,
                              write_timeout=write_timeout)

