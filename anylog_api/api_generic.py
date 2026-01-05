import asyncio

from anylog_api.anylog_rest_api import AnyLogRest
from anylog_api.support import ListCommands


class Generic(ListCommands):
    def __init__(self, anylog_conn:AnyLogRest):
        self.anylog_conn = anylog_conn

    async def async_get_dictionary(self, param:str=None, json_frmt:bool=False, destination:str=None):
        """
        Get dictionary value(s)
        :args:
            param:str - specific AnyLog variable to get value for
            json_frmt:bool - return result in json format
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            either full dict or a specific value based on a given param
        """
        headers = {
            "command": "get dictionary where format=json" if param or json_frmt else "get dictionary",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        response = await self.anylog_conn.async_get(headers)
        if param:
            if destination:
                results = {}
                for node in response:
                    results[node] = response[node].get(param)
            else:
                results = response.get(param)
            response = results

        return response

    def get_dictionary(self, param:str=None, json_frmt:bool=False, destination:str=None):
        """
        Get dictionary value(s)
        :args:
            param:str - specific AnyLog variable to get value for
            json_frmt:bool - return result in json format
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            either full dict or a specific value based on a given param
        """
        return asyncio.run(self.get_dictionary(param, json_frmt, destination))
