"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import ast

import aiohttp
import anylog_api.__support_async__ as support

class AnyLogConnector:
    def __init__(self, conn:str, auth:tuple=(), timeout:int=30):
        """
        The following are the base support for AnyLog via REST
            - GET:extract information from AnyLog (information + queries)
            - POST:Execute or POST command against AnyLog
            - POST_POLICY:POST information to blockchain
        :url:
            https://github.com/AnyLog-co/documentation/blob/master/using%20rest.md
        :param:
            conn:str - REST connection info
            auth:tuple - Authentication information
            timeout:int - REST timeout
        """
        self.conn=conn
        self.auth=None
        if auth:
            self.auth=aiohttp.BasicAuth(*auth)
        self.timeout=timeout

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

        try:
            async with aiohttp.ClientSession(auth=self.auth) as session:
                async with session.get(f'http://{self.conn}', headers=headers, timeout=self.timeout) as response:
                    if response.status < 200 or response.status > 299:
                        error=response.status
                        return await support.extract_get_results(command=command, response=response, error=str(error))
                    return await response.text()
        except Exception as e:
            error=str(e)
            response = False
            return await support.extract_get_results(command=command, response=False, error=str(error))

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

        try:
            async with aiohttp.ClientSession(auth=self.auth) as session:
                async with session.put(f'http://{self.conn}', headers=headers, data=payload, timeout=self.timeout) as response:
                    if response.status < 200 or response.status > 299:
                        return support.validate_put_post('PUT', 'data', False, str(response.status))
                    return True
        except Exception as e:
            return support.validate_put_post('PUT', 'data', False, str(e))

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

        try:
            async with aiohttp.ClientSession(auth=self.auth) as session:
                async with session.post(f'http://{self.conn}', headers=headers, data=payload, timeout=self.timeout) as response:
                    if response.status < 200 or response.status > 299:
                        return support.validate_put_post('POST', 'data', False, str(response.status))
                    return True
        except Exception as e:
            return support.validate_put_post('POST', 'data', False, str(e))


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
