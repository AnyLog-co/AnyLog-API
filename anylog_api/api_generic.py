import ast
import asyncio
from wsgiref.validate import header_re

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
                    try:
                        results[node] = ast.literal_eval(response[node].get(param))
                    except:
                        results[node] = response[node].get(param)
            else:
                try:
                    results = ast.literal_eval(response.get(param))
                except:
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
        return asyncio.run(self.async_get_dictionary(param, json_frmt, destination))

    async def async_set_license(self, license_key:str, destination:str=None):
        """
        Set license key
        :args:
            set_license:str - license key
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        """
        headers = {
            "command": f"set license where activation_key={license_key}",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        await self.anylog_conn.async_post(headers)

    def set_license(self, license_key:str, destination:str=None):
        """
        Set license key
        :args:
            set_license:str - license key
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        """
        asyncio.run(self.async_set_license(license_key, destination))

    async def async_get_license(self, destination:str=None):
        """
        Get license
        :args:
            destination:str - Remote destination
        :params:
            headers:dict - REST headers
        """
        headers = {
            "command": "get license",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        return await self.anylog_conn.async_get(headers)

    def get_license(self, destination:str=None):
        """
        Get license
        :args:
            destination:str - Remote destination
        :params:
            headers:dict - REST headers
        """
        return asyncio.run(self.async_get_license(destination))

    async def async_set_param(self, **kwargs):
        """
        User defined params to add to AnyLog
        :args:
            kwargs:dict - user defined param and corresponding value
            force_set:bool - force using set cmd
        :params:
            headers:dict - REST headers
        """
        headers = {
            "command": None,
            "User-Agent": "AnyLog/1.23"
        }
        if kwargs:
            for name, value in kwargs.items():
                value = ast.literal_eval(value)
                if isinstance(value, bool):
                    headers["command"] = f"set {name}=true" if value else f"set {name}=false"
                elif value.lower() in ["true", "false"]:
                    headers["command"] = f"set {name}=true" if value.lower() == "true" else f"set {name}=false"
                elif isinstance(value, int or float):
                    headers["command"] = f"{name}={value}"
                elif value:
                    headers["command"] = f'set {name}="{value}"'
                else:
                    headers["command"] = f'set {name}=""'
                await self.anylog_conn.async_post(headers)

    def set_param(self, **kwargs):
        """
        User defined params to add to AnyLog
        :args:
            kwargs:dict - user defined param and corresponding value
        :params:
            headers:dict - REST headers
        """
        asyncio.run(self.async_set_param(kwargs))

    async def async_get_hostname(self, destination:str):
        """
        Get hostname for node is running on
        :args:
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            hostname
        """
        headers = {
            "command": "get hostname",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        return await self.anylog_conn.async_get(headers)


    def get_hostname(self, destination:str=None):
        """
        Get hostname for node is running on
        :args:
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            hostname
        """
        return asyncio.run(self.async_get_hostname(destination))
