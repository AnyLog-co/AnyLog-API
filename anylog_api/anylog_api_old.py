import asyncio
from anylog_rest_api import AnyLogRest
from pprint import pprint

class Get(AnyLogRest):
    def __init__(self, conn:str=None, auth:tuple=None, connection_timeout:float=30, read_timeout:float=30,
                 write_timeout:float=30):
        """
        AnyLog REST class for functions associated with `get` requests
        :args:
            conn:str - REST connection information
            auth:tuple - authentication
            connection_timeout:float - TCP connection establishment
            read_timeout:float - Waiting for response data
            write_timeout:float - Sending request data
        """
        super().__init__(conn=conn, auth=auth, connection_timeout=connection_timeout, read_timeout=read_timeout,
                       write_timeout=write_timeout)


    async def __async_exec_get__(self, command:str, destination:str=None, conn:str=None, auth:tuple=None,
                                 connection_timeout:float=None, read_timeout:float=None, write_timeout:float=None):
        """
        Execute `get` request asynchronously
        :args:
            command:str - command to execute
            destination:str - remote destination to run request against
        :overwrite options:
        Option to overwrite default configs
            conn:str - REST connection information
            auth:tuple - authentication
            connection_timeout:float - TCP connection establishment
            read_timeout:float - Waiting for response data
            write_timeout:float - Sending request data
        :params;
            output - extracted results from response
            response - raw response
            headers:dict - REST headers
        :return:
            output
        """
        output = None
        headers = {
            "command": command,
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        response = await self.async_get(headers=headers, conn=conn, auth=auth, connection_timeout=connection_timeout,
                                        read_timeout=read_timeout, write_timeout=write_timeout)

        if response:
            try:
                output = response.json()
            except:
                output = response.text

        return output

    async def async_help(self, anylog_cmd:str=None):
        """
        Execute `help` either in general of a specific command
        """
        command = "help"
        if anylog_cmd:
            command += f" {anylog_cmd}"

        result = await self.__async_exec_get__(command=command)
        pprint(result)


    async def async_get_status(self, json_frmt:bool=False, destination:str=None, conn:str=None, auth:tuple=None,
                               connection_timeout:float=None, read_timeout:float=None, write_timeout:float=None):
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
        command = "get status"
        if json_frmt:
            command += " where format=json"

        return self.__async_exec_get__(command, destination, conn, auth, connection_timeout, read_timeout,
                                       write_timeout)


    def get_status(self, json_frmt:bool=False, destination:str=None, conn:str=None, auth:tuple=None,
                   connection_timeout:float=None, read_timeout:float=None, write_timeout:float=None):

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
        return asyncio.run(self.async_get_status(json_frmt, destination, conn, auth, connection_timeout, read_timeout,
                                                 write_timeout))


    async def async_get_processes(self, json_frmt:bool=False, destination:str=None, conn:str=None, auth:tuple=None,
                                  connection_timeout:float=None, read_timeout:float=None, write_timeout:float=None):
        """
        Execute `get processes`
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
        command = "get processes"
        if json_frmt:
            command += " where format=json"

        return self.__async_exec_get__(command, destination, conn, auth, connection_timeout, read_timeout,
                                       write_timeout)

    def get_processes(self, json_frmt:bool=False, destination:str=None, conn:str=None, auth:tuple=None,
                      connection_timeout:float=None, read_timeout:float=None, write_timeout:float=None):
        """
        Execute `get processes`
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

        return asyncio.run(self.async_get_processes(json_frmt, destination, conn, auth, connection_timeout,
                                                    read_timeout, write_timeout))

    async def async_get_streaming(self):
        pass

    async def async_get_operator(self):
        pass

    async def async_get_publisher(self):
        pass

    async def async_get_scheduler(self):
        pass

    async def async_get_event_log(self):
        pass

    async def async_get_error_log(self):
        pass




