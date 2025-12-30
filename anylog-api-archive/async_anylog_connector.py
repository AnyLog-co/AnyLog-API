"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import ast

import aiohttp
import anylog_api.__support_async__ as support
import json

class AnyLogConnector:
    def __init__(self, conn:str, auth:tuple=(), rest_timeout:float=30, connection_timeout:float=30):
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
            connection_timeout:float - How long to wait for the server to respond when first attempting to connect.
            rest_timeout:float - How long to wait for the server to finish processing and return a response
        """
        self.conn = conn
        if auth and not conn.startswith("http"):
            self.conn=f"https://{conn}"
        elif not conn.startswith("http"):
            self.conn = f"http://{conn}"
        self.auth = auth
        self.rest_timeout = rest_timeout
        self.connection_timeout = connection_timeout


    async def _rest_calls(self, request_type:str, headers:dict, payload:str=None):
        """
               Generic method for sending rest requests
               :args:
                   request_type:str - request type
                   headers:dict request headers
                   payload:str - serialized data
               :params:
                   status:bool
                   response:requests.Response
                   exception_msg:str
               :return:
                   status and response
               """
        status = True
        response = None
        exception_msg = ""
        try:
            async with aiohttp.ClientSession(auth=self.auth) as session:
                if request_type.upper() == "GET":
                    response = session.get(self.conn, headers=headers, timeout=(self.connection_timeout, self.rest_timeout))
                elif request_type.upper() == "PUT":
                    response = session.put(f'http://{self.conn}', headers=headers, data=payload, timeout=(self.connection_timeout, self.rest_timeout))
                elif request_type.upper() == "POST":
                    response = session.post(f'http://{self.conn}', headers=headers, data=payload, timeout=(self.connection_timeout, self.rest_timeout))
                else:
                    exception_msg = f"Invalid request type {request_type}"
                    status = False
                if response:
                    response.raise_for_status()
        except Exception as error:
            exception_msg = f"Failed to execute {request_type.upper()} against {conn} (Error: {error})"
            status = False
        finally:
            if exception_msg:
                raise Exception(exception_msg)

        return [status, response]


    async def get(self, command:str, destination:str=None):
        """
        requests GET command
        :args:
            command:str - command to execute
            destination:str - Remote connection to execute against
        :param:
            headers:dict - REST header information
            response:requests.Response - response from REST request
            error - if request fails, generated error message
        :return:
            if GET generates a result then returns result
            if GET fails then an exception is raised
        """
        error=None
        headers={
            "command":command,
            "User-Agent":"AnyLog/1.23"
        }
        if destination:
            headers['destination']=destination

        status, response = await self._rest_calls(request_type='GET', headers=headers)
        return support.extract_get_results(command=command, response=response, error=error)


    async def put(self, dbms:str, table:str, payload, mode:str='streaming')->bool:
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

        if payload and not isinstance(payload, str):
            serialized_payload = json.dumps(payload)
        else:
            serialized_payload = payload

        status, response = await self._rest_calls(request_type='PUT', headers=headers, payload=serialized_payload)
        return support.validate_put_post(cmd_type='PUT', command='data', response=response, error=error)

    async def post(self, command:str, topic:str=None, destination:str=None, payload=None)->bool:
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
            "command":command,
            "User-Agent":"AnyLog/1.23"
        }
        if topic:
            headers['topic']=topic
        if destination:
            headers['destination']=destination

        if payload and not isinstance(payload, str):
            serialized_payload = json.dumps(payload)
        else:
            serialized_payload = payload

        status, response = await self._rest_calls(request_type='POST', headers=headers, payload=serialized_payload)
        return support.validate_put_post(cmd_type='POST', command='data', response=response, error=error)


def validate_type(anylog_conn):
    """
    Validate input is of type AnyLogConnector
    :args:
        anylog_conn:AnyLogConnector - connection to check
    :raise:
        if invalid raise ValueError
    """
    if not isinstance(anylog_conn, AnyLogConnector):
        raise ValueError(f"Invalid AnyLog connection information")

async def check_status(anylog_conn:AnyLogConnector)->bool:
    """
    Check whether node is running
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-status-command
    :args:
        anylog_conn - connection to AnyLog
    :params:
        status:bool
        output:str - REST request results
    :return:
        True - if accessible
        False - else
    """
    validate_type(anylog_conn=anylog_conn)
    output=await anylog_conn.get("get status where format=json")
    output =ast.literal_eval(output)
    if isinstance(output, dict) and 'Status' in output and 'running' in output['Status'] and 'not running' not in output['Status']:
        return True
    return False


async def get_status(anylog_conn:AnyLogConnector, destination:str=None, json_format:bool=False):
    """
    Execute `get status`
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-status-command
    :args:
        anylog_conn - connection to AnyLog
        destination:str - remote IP and port
        json_format:bool - return results in JSON format
    :params:
        command:str - command to execute
    :return:
        result for `get status`
    """
    validate_type(anylog_conn=anylog_conn)
    command="get status where format=json" if json_format else "get status"
    return await anylog_conn.get(command, destination)


async def get_processes(anylog_conn:AnyLogConnector, json_format:bool=False):
    """
    Execute `get processes`
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-processes-command
    :args:
        anylog_conn - connection to AnyLog
        json_format:bool - return results in JSON format
    :params:
        command:str - command to execute
    :return:
        result for `get processes`
    """
    command="get processes where format=json" if json_format else "get processes"
    return await anylog_conn.get(command)


async def get_connections(anylog_conn:AnyLogConnector, json_format:bool=False):
    """
    Execute `get connections`
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#get-command
    :args:
        anylog_conn - connection to AnyLog
        json_format:bool - return results in JSON format
    :params:
        command:str - command to execute
    :return:
        result for `get connections`
    """
    command="get connections where format=json" if json_format else "get connections"
    return await anylog_conn.get(command)


async def check_node(anylog_conn:AnyLogConnector):
    """
    Check if node is accessible
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/test%20commands.md#test-node
    :args:
        anylog_conn - connection to AnyLog
    :params:
        command:str - command to execute
    :return:
        return status of  node basaed on command (not JSON formata)
    """
    return await anylog_conn.get("test node")


async def check_network(anylog_conn:AnyLogConnector, extra_params:str=None):
    """
    Check if node is accessible
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/test%20commands.md#the-test-network-commands
    :args:
        anylog_conn - connection to AnyLog
        extra_params:str - specific command to support
    :params:
        command:str - command to execute
    :return:
        return status of  node basaed on command (not JSON formata)
    """
    command="test network" if not extra_params else f"test network {extra_params}"
    return await anylog_conn.get(command)
