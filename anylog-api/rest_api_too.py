import asyncio
import os
from typing import Optional, Tuple

import httpx
import support

ROOT_PATH=os.path.dirname(__file__)

_error_resolver=support.NetworkErrorResolver(
    errors=support.load_json(os.path.join(ROOT_PATH, "NETWORK_ERRORS.json")),
    generic=support.load_json(os.path.join(ROOT_PATH, "NETWORK_ERRORS_GENERIC.json")),
)


class AnyLogAPI:
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
        async with httpx.AsyncClient(auth=self.auth, timeout=self.timeout) as client:
            response = await client.request(method=method, url=self.url, headers=headers,
                                            json=payload if isinstance(payload, dict) else None,
                                            content=payload if isinstance(payload, str) else None)

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
        try:
            return asyncio.run(self.async_get_request(command, destination))
        except RuntimeError:
            raise RuntimeError(
                "async_get_request() cannot be used inside an existing event loop"
            )


if __name__ == '__main__':
    api = AnyLogAPI(conn='23.239.12.151:32349')
    print(api.get_request(command="get status"))
    response, err_msg = asyncio.run(api.async_get_request(command="sql cos format=table and stat=false and extend=(+node_name) select count(*) from pp_pm where timestamp >= NOW() - 1 hour", destination="network"))
    print(response)