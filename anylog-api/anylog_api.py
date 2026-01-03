from anylog_api_base import BaseAnyLogAPI

class AnyLogAPI(BaseAnyLogAPI):
    def __init__(self, conn:str, auth:tuple=None, connection_timeout:float=30, read_timeout:float=30,
                 raise_exception:bool=False):
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
        super().__init__(conn, auth, connection_timeout, read_timeout)

    """
    GET requests
    - status
    - processes
    - event log
    - error log
    - scheduler
    - databases
    - msg client
    - exec query
    """
    def get_status(self, json_format:bool=False, destination:str=None):
        """
        Get node status
        :args:
            json_format:bool - whether to return content in json format or not
            destination:str - remote destination to query against
        :params:
            headers:dict - REST headers
            response - response from REST request
            err_msg:str - error message
            output - results from rest request
        :return:
            output, err_msg
        """
        command = "get status"
        if json_format:
            command += " where format=json"

        return self.get_exec(command, destination)

    def get_help(self, anylog_cmd:str=None):
        """
        Get information about command(s)
        :args:
            anylog_cmd:str - AnyLog command
        :print:
            content from help
        """
        command = "help"
        if anylog_cmd:
            command += f" {anylog_cmd}"

        output, err_msg = self.get_exec(command)
        if err_msg:
            raise  err_msg
        if output:
            print(output)

    def get_processes(self, json_format:bool=False, destination:str=None):
        """
        Get running processes
        :args:
            json_format:bool - whether to return content in json format or not
            destination:str - remote destination to get status from
        """
        command = "get processes"
        if json_format:
            command += " where format=json"

        return self.get_exec(command, destination)

    def get_event_log(self, json_format: bool = False, destination: str = None):
        """
        Get event log
        :args:
            json_format:bool - whether to return content in json format or not
            destination:str - remote destination
        """
        command = "get event log"
        if json_format:
            command += " where format=json"

        return self.get_exec(command, destination)

    def get_error_log(self, json_format:bool=False, destination:str=None):
        """
        Get error log
        :args:
            json_format:bool - whether to return content in json format or not
            destination:str - remote destination
        """
        command = "get error log"
        if json_format:
            command += " where format=json"

        return self.get_exec(command, destination)

    def get_scheduler(self, scheduler_id:int=None, destination:str=None):
        """
        Get information about a schedule
        :args:
            scheduler_id:int - schedule ID
            destination:str - remote destination
        """
        command = "get scheduler"
        if scheduler_id:
            command += f"{scheduler_id}"

        return self.get_exec(command, destination)

    def get_databases(self, json_format:bool=False, destination:str=None):
        """
        Get list of databases
        :args:
            json_format:bool - return list in json format
            destination:str - remote destination
        """
        command = "get databases"
        if json_format:
            command += " where format=json"

        return self.get_exec(command, destination)


    def get_msg_client(self, client_id:int=None, topic:str=None, destination:str=None):
        """
        Get msg client(s)
        :args:
            client_id:int - msg client ID
            topic:str - msg client topic
            destination:str - remote destination to
        """
        command = "get msg client"
        if topic:
            command += f' where topic="{topic}"'
        elif client_id:
            command += f" where id={client_id}"

        return self.get_exec(command, destination)
