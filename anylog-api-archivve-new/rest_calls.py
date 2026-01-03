import asyncio
import os
from typing import Optional

import httpx
import support

ROOT_PATH=os.path.dirname(__file__)

_error_resolver=support.NetworkErrorResolver(
    errors=support.load_json(os.path.join(ROOT_PATH, "NETWORK_ERRORS.json")),
    generic=support.load_json(os.path.join(ROOT_PATH, "NETWORK_ERRORS_GENERIC.json")),
)


class RestRequest:
    def __init__(self, conn:str, auth:Optional[tuple]=None, timeout:int=30):
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
        """
        self.url=support.url_builder(conn, is_auth=bool(auth))
        self.auth=auth
        self.timeout=timeout

    def list_commands(self):
        """
        provide docstring / help for fucntions
        """
        return {
            name: getattr(self, name).__doc__
            for name in dir(self)
            if not name.startswith("_") and callable(getattr(self, name))
        }

    async def _request(self, method:str, headers:dict, payload=None)->(httpx.Response, None or str):
        """
        Generic REST request using async request
        :args:
            method:str - request type (GET, PUT, POST)
            headers:dict - REST headers
            payload - content to publish into AnyLog
        :params:
            err_msg:str - Error message
            response:str - request response
        :return:
            response, err_msg
        """
        response = None
        err_msg = None

        # execute request
                # validate
        if response.is_error:
            msg = _error_resolver.resolve(response.status_code)
            err_msg = httpx.HTTPStatusError(f"{method} {self.url} failed ({response.status_code}:{msg})",
                                            request=response.request, response=response)

        return response, err_msg


    async def async_get_request(self, command:str, destination:Optional[str]=None):
        """
        Generic REST request using async request
        :args:
            method:str - request type (GET, PUT, POST)
            headers:dict - REST headers
            payload - content to publish into AnyLog
        :params:
            err_msg:str - Error message
            response:str - request response
        :return:
            response, err_msg
        """
        headers={
            "command":command,
            "User-Agent":"AnyLog/1.23"
        }
        if destination:
            headers["destination"]=destination

        response, err_msg = await self._request("GET", headers)
        if not err_msg:
            response = support.extract_response_content(response)

        return response, err_msg

    def get_request(self, command:str, destination:Optional[str]=None):
        """
        Execute GET requests
        """
        try:
            response, err_msg =  asyncio.run(self.async_get_request(command, destination))
        except RuntimeError:
            err_msg = RuntimeError("async_get_request() cannot be used inside an existing event loop")
            response = None

        return response, err_msg

    async def async_put_request(self, dbms:str, table:str, payload, mode:str='streaming'):
        """
        Execute a PUT command against AnyLog - mainly used for Data
        :args:
            dbms:str - logical database name
            table:str - specific table to store data in
            mode:str - processing data mode (file || streaming)
                --> If invalid raises ValueError on mode
            payload - serialized JSON data to store
        :param:
            headers:dict - REST header information
            response:requests.Response - response from REST request
            error - if request fails, generated error message
        :return:
            if PUT succeed returns True, else returns False
        """
        if mode.lower() not in ['streaming', 'file']:
            raise ValueError(f'Invalid mode option {mode}. Valid options:streaming, file')

        headers={
            'type':'json',
            'dbms':dbms,
            'table':table,
            'mode':mode.lower(),
            'Content-Type':'text/plain'
        }

        return await self._request(method="PUT", headers=headers, payload=payload)


    def put_request(self, dbms:str, table:str, payload, mode:str='streaming'):
        try:
            response, err_msg = asyncio.run(self.async_put_request(dbms, table, payload, mode))
        except RuntimeError:
            err_msg = RuntimeError("async_put_request() cannot be used inside an existing event loop")
            response = None

        return response, err_msg

    async def async_post_request(self, command:str, topic:str=None, destination:str=None, payload=None):
        """
        Execute POST command against AnyLog. payload is required under the following conditions:
            1. payload can be data that you want to add into AnyLog, in which case you should also have an
                MQTT client of type REST running on said node
            2. payload can be a policy you'd like to add into the blockchain
            3. payload can be a policy you'd like to remove from the blockchain
                note only works with Master, cannot remove a policy on a real blockchain like Ethereum.
        :args:
            command:str -  command to execute
            topic:str - when sending data via POST, the associated table name
             destination:sstr - Remote connection to execute against
            payload - serialized JSON data to store
        :param:
            headers:dict - REST header information
            response:requests.Response - response from REST request
            error - if request fails, generated error message
        :return:
            if POST succeed returns True, else returns False
        """
        headers={
            "command": command,
            "User-Agent":"AnyLog/1.23"
        }
        if topic:
            headers['topic'] = topic
        if destination:
            headers['destination'] = destination

        return await self._request(method="POST", headers=headers, payload=payload)


    def post_request(self, command:str, topic:str=None, destination:str=None, payload=None):
        try:
            response, err_msg = asyncio.run(self.async_post_request(command, topic, destination, payload))
        except RuntimeError:
            err_msg = RuntimeError("async_postrequest() cannot be used inside an existing event loop")
            response = None

        return response, err_msg


if __name__ == '__main__':
    api = RestRequest(conn='23.239.12.151:32349')
    print(api.get_request(command="get status"))
    response, err_msg = asyncio.run(api.async_get_request(command="sql cos format=table and stat=false and extend=(+node_name) select count(*) from pp_pm where timestamp >= NOW() - 1 hour", destination="network"))
    print(response)