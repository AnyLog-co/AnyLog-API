import asyncio
from anylog_api.anylog_rest_api import AnyLogRest
from anylog_api.support import ListCommands


class Logging(ListCommands):
    def __init__(self, anylog_conn:AnyLogRest):
        self.anylog_conn=anylog_conn

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
        headers={
            "command":"get event log where format=json" if json_frmt else "get event log",
            "User-Agent":"AnyLog/1.23",
            "destination":destination if destination else ""
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

    async def async_reset_event_log(self, destination:str=None):
        """
        reset event log
        :args:
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        """
        headers={
            "command":"reset error log",
            "User-Agent":"AnyLog/1.23",
            "destination":destination if destination else ""
        }

        await self.anylog_conn.async_post(headers=headers,payload=None)

    def reset_event_log(self, destination:str=None):
        """
        reset event log
        :args:
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        """
        asyncio.run(self.async_reset_event_log(destination))

    async def async_get_error_log(self, json_frmt:bool=False, destination:str=None):
        """
        View error log
        :args:
            json_frmt:bool - return results in JSON format
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            error log
        """
        headers={
            "command":"get error log where format=json" if json_frmt else "get error log",
            "User-Agent":"AnyLog/1.23",
            "destination":destination if destination else ""
        }

        return await self.anylog_conn.async_get(headers=headers)

    def get_error_log(self, json_frmt:bool=False, destination:str=None):
        """
        View error log
        :args:
            json_frmt:bool - return results in JSON format
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            error log
        """
        return asyncio.run(self.async_get_error_log(json_frmt, destination))

    async def async_reset_error_log(self, destination:str=None):
        """
        reset error log
        :args:
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        """
        headers={
            "command":"reset error log",
            "User-Agent":"AnyLog/1.23",
            "destination":destination if destination else ""
        }

        await self.anylog_conn.async_post(headers=headers, payload=None)

    def reset_error_log(self, destination:str=None):
        """
        reset event log
        :args:
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        """
        asyncio.run(self.async_reset_error_log(destination))

    async def async_enable_echo_queue(self, destination:str=None):
        """
        Enable echo queue
        :args:
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        """
        headers={
            "command":"set echo queue on",
            "User-Agent":"AnyLog/1.23",
            "destination": destination if destination else ""
        }

        await self.anylog_conn.async_post(headers=headers, payload=None)

    def enable_echo_queue(self, destination:str=None):
        """
        Enable echo queue
        :args:
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        """
        asyncio.run(self.async_enable_echo_queue(destination))

    async def async_disable_echo_queue(self, destination:str=None):
        """
        Disable echo queue
        :args:
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        """
        headers={
            "command":"set echo queue off",
            "User-Agent":"AnyLog/1.23",
            "destination": destination if destination else ""
        }

        await self.anylog_conn.async_post(headers=headers, payload=None)

    def disable_echo_queue(self, destination:str=None):
        """
        Disable echo queue
        :args:
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        """
        asyncio.run(self.async_disable_echo_queue(destination))

    async def async_reset_echo_queue(self, queue_size:int=20, destination:str=None):
        """
        Reset echo queue (size)
        :args:
            queue_size:int - queue size (default 20)
            destination:str - remote destination
        :params;
            headers:dict - REST headers
        """
        headers = {
            "command": f"reset echo queue where size={queue_size}",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        await self.anylog_conn.async_post(headers=headers, payload=None)

    def reset_echo_queue(self, queue_size:int=20, destination:str=None):
        """
        Reset echo queue (size)
        :args:
            queue_size:int - queue size (default 20)
            destination:str - remote destination
        :params;
            headers:dict - REST headers
        """
        asyncio.run(self.async_reset_echo_queue(queue_size, destination))

    async def async_get_echo_queue(self, destination:str=None):
        """
        Get echo queue
        :args:
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            echo queue
        """
        headers = {
            "command": "get echo queue",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        return await self.anylog_conn.async_get(headers=headers)

    def get_echo_queue(self, destination:str=None):
        """
        Get echo queue
        :args:
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            echo queue
        """
        return asyncio.run(self.async_get_echo_queue(destination))

