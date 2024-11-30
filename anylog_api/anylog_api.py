import warnings
import webbrowser

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union

import anylog_api.anylog_connector as anylog_connector
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.__support__ import json_dumps


class AnyLogAPI:
    def __init__(self, conn:str, timeout:int=30, exception:bool=False):
        """
        :args:
            conn:str - REST connection credentials (ex. IP:PORT | {USER}:{PASSWORD}@{IP}:{PORT} )
            timeout:int - REST timeout
            exception:bool - whether to print/raise exceptions
        :params:
            self.anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog
            self.exception:bool - whether to print/raise exceptions
        """
        self.exception = exception
        self.anylog_conn = anylog_connector.AnyLogConnector(conn=conn, timeout=timeout)


    def __post_data(self, headers:dict, payload:dict, topic:str, view_help:bool=False)->Union[bool, None]:
        """
        Execute POST for (JSON) data
        :args:

            headers:dict - REST headers
            payload - data to publish into AnyLog
            topic:str - msg client topic
            view_help:bool - get help regarding command
            exception:bool -
        :params:
            status:bool
        :return:
            if view_help is True --> None
            True -->  success
            False --> fails
        """
        status = None
        if topic:
            headers['topic'] = topic
        headers['Content-Type'] = 'text/plain'

        if isinstance(payload, list):
            serialize_data = [json_dumps(content=row, exception=self.exception) for row in payload]
        elif isinstance(payload, dict):
            serialize_data = json_dumps(content=payload, exception=self.exception)
        else:
            serialize_data = payload

        if view_help is True:
            url = 'https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#data-transfer-using-a-rest-api'
            try:
                # Try to open the URL in the default web browser
                if not webbrowser.open(url):
                    raise webbrowser.Error(f'Failed to open browser to documentation: {url}')
            except Exception as error:
                raise webbrowser.Error(f'Failed to open browser to documentation: {url} (Error: {error})')
        else:
            status = execute_publish_cmd(conn=self.anylog_conn, cmd='POST', headers=headers, payload=serialize_data,
                                         exception=self.exception)

        return  status


    def __post_params(self, params:dict, destination:str=None, view_help:bool=False)->None:
        """
        Publish key:value pairs into AnyLog/EdgeLake dictionary
        :args:
            params: given a set of params (payload values) set said values into AnyLog/EdgeLake dictionary
            destination:str - remote destination connection information to data to
            view_help:bool - get help regarding command
        :params:
            status:bool
            headers:dict - REST headers
        :return:
            None
        """
        headers = {
            "User-Agent": "AnyLog/1.23"
        }
        if destination:
            headers['destination'] = destination

        # Define a function to handle the command execution for each key-value pair
        def execute_command(key, value):
            if value in ['false', 'False', 'True', 'true', 'file']:
                command = f'set {key.strip()} = {value.strip()}'
            elif value != "":
                command = f'{key.strip()} = {value.strip()}'
            else:
                return  # Skip empty values
            headers['command'] = command

            if view_help:
                self.get_help(cmd=command, get_index=False)
            else:
                execute_publish_cmd(conn=self.anylog_conn, cmd='post', headers=headers, payload=None, exception=self.exception)

        # Use ThreadPoolExecutor with a maximum of 10 threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit each command as a task to the executor
            futures = [executor.submit(execute_command, key, params[key]) for key in params]

            # Wait for all futures to complete
            for future in as_completed(futures):
                # Optionally handle any exceptions
                try:
                    future.result()  # We could check results or exceptions here if needed
                except Exception as e:
                    if self.exception:
                        raise Exception(f"Exception during command execution: {e}")


    def __post_cmd(self, headers:dict, payload:dict=None, destination:str=None, view_help:bool=False)->Union[bool, None]:
        """
        Execute PUBLISH command against AnyLog/EdgeLake
        :args:
            headers:dict - REST headers
            payload - blockchain policy
            destination:str - remote destination connection information to data to
            view_help:bool - get help regarding command
        :params:
            status:bool
        :return:
            if view_help is True --> None
            else ->
                True -->  success
                False --> fails
        """
        status = None
        if destination:
            headers['destination'] = destination

        if view_help is True:
            self.get_help(cmd=headers['command'], get_index=False)
        else:
            status = execute_publish_cmd(conn=self.anylog_conn, cmd='post', headers=headers, payload=payload, exception=self.exception)

        return status


    def get_help(self, cmd:str=None, get_index:bool=False)->None:
        """
        Get help information about command
        :url:
            https://github.com/AnyLog-co/documentation/blob/master/getting%20started.md#the-help-command
        :args:
            cmd:str - command to get help with
            is_index:bool - get index information for a "topic"
        :params:
            output:str - results
            headers:dict - REST headers
        :output:
            prints help information for a given command
        """
        index_options = ['api', 'background processes', 'blockchain', 'cli', 'config', 'configuration', 'data', 'dbms',
                         'debug', 'enterprise', 'file', 'help', 'high availability', 'index', 'internal', 'json', 'log', 'metadata',
                         'monitor', 'node info', 'profile', 'profiling', 'query', 'script', 'secure network', 'streaming',
                         'test suite', 'unstructured data']
        headers = {
            "command": "help",
            "User-Agent": "AnyLog/1.23",
        }

        if get_index is True and cmd in index_options:
            headers['command'] += f" index {index_options}"
        elif get_index is True and not cmd:
            headers['command'] += f" index"
        else:
            if get_index is True and cmd not in index_options and self.exception is True:
                warnings.warn(f'Invalid option for indexing, providing regular help.\nSupported cmds for indexing: {",".join(index_options)}')
            headers['command'] += f" {cmd}"

        if cmd is not None:
            headers['command'] += " " + cmd

        output = extract_get_results(conn=self.anylog_conn, headers=headers, exception=self.exception)
        print(f"Inputted Command: {headers['command']} \n{output}")


    def get_status(self, destination:str=None, view_help:bool=False)->Union[bool, None]:
        """
        Check whether node is running
        :url:
            https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-status-command
        :args:
            destination:str - Remote node to query against
            view_help:bool - get information about command
        :params:
            status:bool - whether node is accessible
            headers:dict - REST headers
            output:str - results
        :return:
            is return_cmd is True -> the return command
            else ->
                True - node accessible
                False - node not accessible
        """
        status = None
        headers = {
            "command": "get status where format=json",
            "User-Agent": "AnyLog/1.23"
        }

        if destination is not None:
            headers["destination"] = destination

        if view_help is True:
            self.get_help(cmd=headers['command'])
        else:
            status = False
            output = extract_get_results(conn=self.anylog_conn, headers=headers, exception=False)
            if isinstance(output, dict) and 'Status' in output and ('not' not in output['Status'] and 'running' in output['Status']):
                status = True
            elif isinstance(output, str) and ('not' not in output and 'running' in output):
                status = True

        return status


    def execute_get(self, command:str, destination:str=None, view_help:bool=False):
        """
        Execute GET command against AnyLog/EdgeLake
        -> if SQL command, then extend to have destination param in headers
        :args:
            command:str - command to execute via REST
            destination:str - Remote node to query against
            view_help:bool - get information about command
        :params:
            output
            headers:dict - REST headers
        :return:
            if view_help -> None
            else -> result from GET request
        """
        output = None
        headers = {
            "command": command,
            "User-Agent": "AnyLogg/1.23"
        }

        if "sql" == command.split()[0] and destination:
            headers['destination'] = destination
        elif "sql" == command.split()[0] and "system_query" != command.split()[1] and not destination:
            headers['destination'] = "network"

        if view_help is True:
            self.get_help(cmd=headers['command'], get_index=False)
        else:
            output = extract_get_results(conn=self.anylog_conn, headers=headers, exception=self.exception)

        return output


    def put_data(self, payload, db_name:str, table_name:str, mode:str='streaming', view_help:bool=False):
        """
        Insert data into EdgeLake / AnyLog via PUT
        :args:
            payload - dict or list of data to insert (will automatically serialize if not string)
            db_name:str - logical database to store data in
            table_name:str - table to store data in (within logical database)
            mode:bool - whether to send data using streaming of file
            view_help:bool - get help regarding command
        :params:
            status:bool
            headers:dict - REST headers
            serialize_data - serialized data
        :return:
            if return_cmd is True --> headers
            True -->  data sent
            False --> Fails to send data
        """
        status = None
        headers = {
            'command': 'data',
            'dbms': db_name,
            'table': table_name,
            'mode': mode,
            'User-Agent': 'AnyLog/1.23',
            'Content-Type': 'text/plain'
        }

        if mode not in ['streaming', 'file']:
            headers['mode'] = 'streaming'
            if self.exception is True:
                warnings.warn(f"Warning: Invalid mode format {mode}. Options: streaming (default), file ")

        serialize_data = json_dumps(content=payload, exception=self.exception)

        if view_help is True:
            url = 'https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#data-transfer-using-a-rest-api'
            try:
                # Try to open the URL in the default web browser
                if not webbrowser.open(url):
                    raise webbrowser.Error(f'Failed to open browser to documentation: {url}')
            except Exception as error:
                raise webbrowser.Error(f'Failed to open browser to documentation: {url} (Error: {error})')
        else:
            status = execute_publish_cmd(conn=self.anylog_conn, cmd='PUT', headers=headers, payload=serialize_data, exception=self.exception)

        return status


    def execute_post(self, command:str, payload:Union[dict, list]=None, topic:str=None, destination=None,
                     view_help:bool=False):
        """
        Execute PUBLISH command against AnyLog/EdgeLake
        -> command
        -> data
        -> blockchain
        :args:
            command:str - command to execute
                - data: POST data into the node
                - params: given a set of params (payload values) set said values into AnyLog/EdgeLake dictionary
                - any other command that requires a POST, such as
                    -> blockchain publish
                    -> run msg client
                    -> run scheduler
            payload - payload content to be used with PUBLISH process. Such as
                -> blockchain policy
                -> data to publish into AnyLog
                -> key:value pairs (dict) to be stored into AnyLog dictionary
            topic:str - msg client topic
            destination:str - remote destination connection information to data to
            view_help:bool - get help regarding command
        :params:
            status:bool
            headers:dict - REST headers
        :return:
            if view_help is True --> None
            True -->  success
            False --> fails
        """
        status = None
        headers = {
            "command": command,
            "User-Agent": "AnyLog/1.23"
        }

        if command == 'data':
            status = self.__post_data(headers=headers, payload=payload, topic=topic, view_help=view_help)
        elif command == 'params':
            self.__post_params(params=payload, destination=destination, view_help=view_help)
        else:
            status = self.__post_cmd(headers=headers, payload=payload, destination=destination, view_help=view_help)

        return status
