import httpx
import asyncio
from abc import ABC, abstractmethod
from httpx import NetworkError
import os

from support import url_builder, load_json

ROOT_PATH = os.path.dirname(__file__)

NETWORK_ERRORS = load_json(file_path=os.path.join(ROOT_PATH, "NETWORK_ERRORS.json"))
NETWORK_ERRORS_GENERIC = load_json(file_path=os.path.join(ROOT_PATH, "NETWORK_ERRORS_GENERIC.json"))


class BaseAnyLogAPI(ABC):
    def __init__(self, conn:str, auth:tuple=None, connection_timeout:float=30, read_timeout:float=30,
                 raise_exception:bool=False):
        """
        The following are the base support for AnyLog via REST
            - GET: extract information from AnyLog (information + queries)
            - POST: Execute or POST command against AnyLog
            - POST_POLICY: POST information to blockchain
        :url:
            https://github.com/AnyLog-co/documentation/blob/master/using%20rest.md
        :param:
            conn:str - REST connection info
            auth:tuple - Authentication information
            timeout:int - REST timeout
            raise_exception:bool - whether for API to raise exception when failing
        """
        self.url = url_builder(conn, is_auth=bool(auth))
        self.auth = auth
        self.timeout = httpx.Timeout(connect=connection_timeout, read=read_timeout)
        self.raise_exception = raise_exception

    async def async_exec_request(self, exec_type:str, headers:dict, payload=None):
        """
        Execute REST request against AnyLog/EdgeLake
        :args:
            exec_type:str - REST request type
            headers:dct - REST headers
            payload - content to publish
        :params:
            response - request response
            err_msg:str - error if request fails
        :return:
            response, err_msg
        """
        response = None
        err_msg = None
        try:
            async with httpx.AsyncClient(auth=self.auth, timeout=self.timeout) as client:
                response = await client.request(method=exec_type.upper(), url=self.url, headers=headers,
                                                json=payload if isinstance(payload, dict) else None,
                                                content=payload if isinstance(payload, str) else None)
                status_code = str(response.status_code)
                if response and not 200 <= int(response.status_code) < 300:
                    status_code_str="UNKNOWN"
                    if NETWORK_ERRORS.get(status_code):
                        status_code_str = NETWORK_ERRORS.get(response.status_code)
                    elif NETWORK_ERRORS_GENERIC.get(status_code):
                        status_code_str = NETWORK_ERRORS_GENERIC.get(status_code[0])

                    err_msg = NetworkError(f"Failed to execute {exec_type.upper()} request against {self.url} (Network Error {int(status_code)}: {status_code_str})")
        except Exception as error :
            err_msg = Exception(f"Failed to execute GET against {self.url} (Error: {error})")

        if err_msg and self.raise_exception:
            raise err_msg

        return response, err_msg

    def exec_request(self, exec_type:str, headers:dict, payload=None):
        """
        Execute asynchronicity `exec_request` without it being async
         :args:
            exec_type:str - REST request type
            headers:dct - REST headers
            payload - content to publish
        :params:
            response - request response
            err_msg:str - error if request fails
        :return:
            response, err_msg
        """
        return asyncio.run(self.async_exec_request(exec_type=exec_type, headers=headers, payload=payload))

    async def async_get_exec(self, command:str, destination:str=None):
        """
        Execute GET request(s)
        :args:
            command:str - REST command to execute
            destination:str - remote destination to send request against
        :params:
            output - request results
            headers:dict - REST headers
            response, err_msg - response from rest request
        :return:
            output, err_msg
        """
        output = None
        headers = {
            "command": command,
            "User-Agent": "AnyLog/1.23",
        }
        if destination:
            headers["destination"] = destination

        response, err_msg = await self.async_exec_request(exec_type="GET", headers=headers, payload=None)
        if not err_msg and response :
            try:
                output = response.json()
            except:
                output = response.text

        return output, err_msg

    def get_exec(self, command:str, destination:str=None):
        """
        Execute GET request(s)
        :args:
            command:str - REST command to execute
            destination:str - remote destination to send request against
        :params:
            output - request results
            headers:dict - REST headers
            response, err_msg - response from rest request
        :return:
            output, err_msg
        """
        return asyncio.run(self.async_get_exec(command=command, destination=destination))

    def list_commands(self):
        """
        provide docstring / help for functions
        """
        return {
            name: getattr(self, name).__doc__
            for name in dir(self)
            if not name.startswith("_") and callable(getattr(self, name))
        }

    """
    GET requests
    - status
    - processes
    - event log
    - error log
    - scheduler
    - databases
    - msg client
    - exec query
    """
    @abstractmethod
    def get_status(self, json_format:bool=False, destination:str=None):
        """
        Get node status
        :args:
            json_format:bool - whether to return content in json format or not
            destination:str - remote destination to query against
        """
        return _, NotImplemented

    @abstractmethod
    def get_help(self, anylog_cmd:str=None):
        """
        Get information about command(s)
        :args:
            anylog_cmd:str - AnyLog command
        :print:
            content from help
        """
        return _, NotImplemented

    @abstractmethod
    def get_processes(self, json_format:bool=False, destination:str=None):
        """
        Get running processes
        :args:
            json_format:bool - whether to return content in json format or not
            destination:str - remote destination to get status from
        """
        return _, NotImplemented

    @abstractmethod
    def get_event_log(self, json_format: bool = False, destination: str = None):
        """
        Get event log
        :args:
            json_format:bool - whether to return content in json format or not
            destination:str - remote destination
        """
        return _, NotImplemented

    @abstractmethod
    def get_error_log(self, json_format:bool=False, destination:str=None):
        """
        Get error log
        :args:
            json_format:bool - whether to return content in json format or not
            destination:str - remote destination
        """
        return _, NotImplemented

    @abstractmethod
    def get_scheduler(self, scheduler_id:int=None, destination:str=None):
        """
        Get information about a schedule
        :args:
            scheduler_id:int - schedule ID
            destination:str - remote destination
        """
        return _, NotImplemented

    @abstractmethod
    def get_databases(self, json_format:bool=False, destination:str=None):
        """
        Get list of databases
        :args:
            json_format:bool - return list in json format
            destination:str - remote destination
        """
        return _, NotImplemented

    @abstractmethod
    def get_msg_client(self, client_id:int=None, topic:str=None, destination:str=None):
        """
        Get msg client(s)
        :args:
            client_id:int - msg client ID
            topic:str - msg client topic
            destination:str - remote destination to
        """
        return _, NotImplemented

    # class PostFunctions:
    #     """
    #     POST requests
    #     - Insert Data
    #     - Insert Policies
    #     - run msg client
    #     - connect dbms
    #     """
    #
    #     @abstractmethod
    #     def run_msg_client(self, broker:str, port:int, topic:str="#", user:str=None, password:str=None, enable_logs:bool=False,
    #                        policy_id:str=None, db_name:str=None, table_name:str=None, columns:dict={}):
    #         """
    #         Execute `run msg client`
    #         :args:
    #             broker:str - broker IP address
    #             port:int - broker port
    #             topic:str - MQTT topic
    #             user:str - user to access MQTT
    #             password:str - password associated with user
    #             enable_logs:bool - logs for MQTT
    #
    #             # Option 1 - Policy based
    #             policy_id:str - blockchain policy ID to map data with
    #
    #             # Option 2 - manual mapping
    #             db_name:str - logical database name
    #             table_name::str - logical table name
    #             columns:dict - mapping columns (format: {"column_name": {"value_type": column data type, "bring_cmd": extraction cmd} )
    #         """
    #         return _, NotImplemented
    #
    # @abstractmethod
    # def insert_data(self, payload, topic:str):
    #     """
    #     Insert data via POST
    #     :args:
    #         payload - content to publish into AnyLog
    #
    #     """
