import fastapi
from rest_calls import RestRequest
from pprint import pprint


FASTAPI_ENABLED = False
FAST_API = None

def enable_fastapi():
    global FASTAPI_ENABLED
    global FAST_API

    FASTAPI_ENABLED = True
    FAST_API = fastapi.FastAPI()


class AnyLogAPI(RestRequest):
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
            is_async:bool -
        """
        super().__init__(conn=conn, auth=auth, timeout=timeout)
        if enable_fastapi:
            enable_fastapi()

    def get_status(self, is_json:bool=False, destination:str=""):
        """
        Execute `get status`
        """
        command = "get status"
        if is_json:
            command += " where format=json"

        response, err_msg = self.get_request(command=command, destination=destination)
        if err_msg:
            raise Exception(err_msg)
        return response

    def get_connections(self, is_json:bool=False, destination:str=None):
        """
        Get connection information
        """
        command = "get connections"
        if is_json:
            command += " where format=json"

        response, err_msg = self.get_request(command=command, destination=destination)
        if err_msg:
            raise Exception(err_msg)

        return response

    def get_processes(self, is_json:bool=False, destination:str=None):
        """
        Get list of services and whether they are running or not
        """
        command = "get processes"
        if is_json:
            command += " where format=json"

        response, err_msg = self.get_request(command=command, destination=destination)
        if err_msg:
            raise Exception(err_msg)
        return response

    def get_event_log(self, is_json:bool=False, destination:str=None):
        """
        Get list of events
        """
        command = "get event log"
        if is_json:
            command += " where format=json"

        response, err_msg = self.get_request(command=command, destination=destination)
        if err_msg:
            raise Exception(err_msg)

        return response

    def get_error_log(self, is_json:bool=False, destination:str=None):
        """
        Get list of errors
        """
        command = "get error log"
        if is_json:
            command += " where format=json"

        response, err_msg = self.get_request(command=command, destination=destination)
        if err_msg:
            raise Exception(err_msg)

        return response

    def get_echo_queue(self, is_json:bool=False, destination:str=None):
        """
        Get echo queue
        """
        command = "get echo queue"
        if is_json:
            command += " where format=json"

        response, err_msg = self.get_request(command=command, destination=destination)
        if err_msg:
            raise Exception(err_msg)

        return response

    def get_scheduler(self, schedule_id:int=None, destination:str=None):
        """
        get running scheduler processes
        """
        command = "get scheduler"
        if schedule_id:
            command += f" {schedule_id}"

        response, err_msg = self.get_request(command, destination=destination)
        if err_msg:
            raise Exception(err_msg)
        return response

    def test_node(self):
        """
        Test node status
        """
        command = "test node"
        response, err_msg = self.get_request(command=command)
        if err_msg:
            raise Exception(err_msg)

        return response

    def test_network(self):
        """
        Test network status
        """
        command = "test network"
        response, err_msg = self.get_request(command=command)
        if err_msg:
            raise Exception(err_msg)

        return response

    def query_data(self, db_name:str, query:str, output_format:str="json", stat:bool=True,
                   include_tables=None, extend_query=None, destination:str="network"):
        """
        Execute SQL query against AnyLog / EdgeLake
        :args:
            db_name:str - logical database name
            query:str - SELECT statement
            output_format:str - output format
                - json
                - json:list
                - table
            stat:bool - include statistics in output
            include_tables - list, tuple or comma separated string of (other) tables to include in the command
            extend_query - list, tuple or comma separated string of information to include in the command
            destination:str - node(s) to query against
        :params:
            command:str - command to execute
        """
        if destination == "local":
            destination = ""

        command = f"sql {db_name}"
        if output_format.lower() in ["json", "json:list", "table"]:
            command += f" format={output_format} and"
        if stat is False or (isinstance(stat, str) and stat.lower() == "false"):
            command += f" stat=false and"
        if include_tables:
            if isinstance(include_tables, list or tuple):
                include_tables = ",".join(include_tables)
            command += f" include=({include_tables}) and"
        if extend_query:
            if isinstance(extend_query, list or tuple):
                extend_query = ",".join(extend_query)
            command += f" extend=({extend_query}) and"

        command = f'{command.rsplit("and", 1)} "{query}"'

        response, err_msg = self.get_request(command, destination)
        if err_msg:
            raise Exception(err_msg)

        return response

    def run_msg_client(self, broker:str, port:int, topic:str="#", user:str=None, password:str=None, policy_id:str=None,
                       db_name:str=None, table:str=None, columns:dict=None, destination:str=None):
        """
        Initiate `run msg client`
        :command:
        <run msg client where
            broker=mybroker.org and
            port=8172 and
            user=demouser and
            password=demopass and
            log=false and
            topic=(
                name=new-topic andk
                policy=anylog-policy3
            )>
        :args:
            broker:str - broker ip
            port:int - mqtt port
            topic:str = topic name
            user:str - user to connect to msg client
            password:str - password associated with user

            # policy mapping
            policy_id:str - blockchain policy to map MQTT to table

            # standard mapping
            db_name:str - logical database
            table:str - table to store
            columns:dict - columns to store data
                {"column_name": {
                    "value_type": "str" or "int" or "float" or "bool" or "timestamp",
                    "bring_value": "bring [column]"
                }}

            destination:str - remote destination(s) to send request against
        :params:
            command:str - command to execute
        """
        command = f"run msg client where broker={broker} and port={port}"
        if user:
            command += f" and user={user}"
        if password:
            command += f" and password={password}"
        command += f" and log=false  and topic=(name={topic}"
        if policy_id:
            if pid in policy_id.split(","):
                command += f" and policy={pid}"
        else:
            if db_name:
                command += f" and dbms={db_name}"
            if table:
                command += f" and table={table}"
            if columns:
                for column in columns:
                    data_type = columns.get(column).get("value_type") if columns.get(column).get("value_type") else "str"
                    if data_type not in ["str", "int", "float", "bool", "timestamp"]:
                        raise Exception(f"Invalid column type...")
                    if data_type == "string":
                        data_type = "str"
                    bring_value = columns.get(column).get("bring_value")
                    if bring_value:
                        command += f' and column.{column}.{data_type}="{bring_value}"'
        command += ")"

        response, err_msg = self.post_request(command=command, destination=destination)
        if not err_msg:
            raise Exception(err_msg)
        return response

    def get_msg_client(self):




if __name__ == '__main__':
    anylog_api = AnyLogAPI(conn="23.239.12.151:32349")
    pprint(anylog_api.list_commands())