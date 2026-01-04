import asyncio
from anylog_api.anylog_rest_api import AnyLogRest

class Logging:
    def __init__(self, anylog_conn:AnyLogRest):
        self.anylog_conn = anylog_conn

    async def async_get_event_log(self, json_frmt:bool=False, destination:str=None):
        """
        View event log
        :args:
            json_frmt:bool - return results in JSON format
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            event log
        """
        headers = {
            "command": "get event log where format=json" if json_frmt else "get event log",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        return await self.anylog_conn.async_get(headers=headers)

    def get_event_log(self, json_frmt:bool=False, destination:str=None):
        """
        View event log
        :args:
            json_frmt:bool - return results in JSON format
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            event log
        """
        return asyncio.run(self.async_get_event_log(json_frmt, destination))