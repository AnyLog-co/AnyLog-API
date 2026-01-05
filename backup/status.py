import asyncio
from anylog_api.anylog_rest_api import AnyLogRest
from anylog_api.list_cmds import ListCommands


class Status(ListCommands):
    def __init__(self, anylog_conn:AnyLogRest):
        self.anylog_conn = anylog_conn


    async def async_get_status(self, json_frmt:bool=False, destination:str=None):
        """
        Execute `get status`
        :args:
            json_format:str - return results in JSON format
            destination:str - remote destination to run request against
        :overwrite options:
        Option to overwrite default configs
            conn:str - REST connection information
            auth:tuple - authentication
            connection_timeout:float - TCP connection establishment
            read_timeout:float - Waiting for response data
            write_timeout:float - Sending request data
        :params:
            command:str - command to execute
        :return:
            results from `get status`
        """
        headers = {
            "command": "get status where format=json" if json_frmt else "get status",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        return await self.anylog_conn.async_get(headers)

    def get_status(self, json_frmt:bool=False, destination:str=None):
        """
        Execute `get status`
        :args:
            json_format:str - return results in JSON format
            destination:str - remote destination to run request against
        :overwrite options:
        Option to overwrite default configs
            conn:str - REST connection information
            auth:tuple - authentication
            connection_timeout:float - TCP connection establishment
            read_timeout:float - Waiting for response data
            write_timeout:float - Sending request data
        :params:
            command:str - command to execute
        :return:
            results from `get status`
        """
        return asyncio.run(self.async_get_status(json_frmt=json_frmt, destination=destination))


    async def async_test_node(self):
        """
        Test node status
        :args:
        :params:
            headers:dict - REST headers
        :return:
            results from tet node
        """
        headers = {
            "command": "test node",
            "User-Agent": "AnyLog/1.23"
        }

        return await self.anylog_conn.async_get(headers=headers)


    def test_node(self):
        """
        Test node status
        :args:
        :params:
            headers:dict - REST headers
        :return:
            results from tet node
        """
        return asyncio.run(self.async_test_node())

    async def async_test_network(self):
        """
        Test network status
        :args:
        :params:
            headers:dict - REST headers
        :return:
            results from tet node
        """
        headers = {
            "command": "test network",
            "User-Agent": "AnyLog/1.23"
        }

        return await self.anylog_conn.async_get(headers=headers)

    def test_network(self):
        """
        Test network status
        :args:
        :params:
            headers:dict - REST headers
        :return:
            results from tet network
        """
        return asyncio.run(self.async_test_network())
