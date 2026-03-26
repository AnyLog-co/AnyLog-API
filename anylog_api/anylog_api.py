import os

from anylog_api.anylog_rest_api import AnyLogRest
from anylog_api.api_node_status import Status
from anylog_api.api_logs import Logging
from anylog_api.api_process import Processes
from anylog_api.api_blockchain import Blockchain
from anylog_api.api_dbms import DBMS
from anylog_api.api_data import Data
from anylog_api.api_data_aggregation import DataAggregation
from anylog_api.api_southbound import Southbound
from anylog_api.api_generic import Generic

class AnyLogAPI:
    def __init__(self, conn:str, auth:tuple=None, connection_timeout:float=30, read_timeout:float=30,
                 write_timeout:float=30):
        """
        "main" for AnyLlog API
        :args:
            conn:str - connection IP:port
            auth:tuple - authentication information
            connection_timeout:float
            read_timeout:float
            write_timeout:float
        :params:
            self.conn - connection to AnyLog / Edgelake
        """
        self.anylog_conn = AnyLogRest(conn=conn, auth=auth, connection_timeout=connection_timeout,
                                      read_timeout=read_timeout, write_timeout=write_timeout)

        # API configurations
        self.help = self.anylog_conn.help
        self.exec_mode = self.anylog_conn.exec_mode
        self.update_exec_mode = self.anylog_conn.update_exec_mode

        # Functions
        self.generic = Generic(anylog_conn=self.anylog_conn)
        self.node_status = Status(anylog_conn=self.anylog_conn)
        self.logging = Logging(anylog_conn=self.anylog_conn)
        self.processes = Processes(anylog_conn=self.anylog_conn)
        self.blockchain = Blockchain(anylog_conn=self.anylog_conn)
        self.dbms = DBMS(anylog_conn=self.anylog_conn)
        self.data = Data(anylog_conn=self.anylog_conn)
        self.data_aggregation = DataAggregation(anylog_conn=self.anylog_conn)
        self.southbound = Southbound(anylog_conn=self.anylog_conn)

        # Help
        self.modules = {
            # 1. Connectivity / core
            "anylog_conn": {
                "path": os.path.join("anylog_api", "anylog_rest_api.py"),
                "functions": self.anylog_conn.list_commands(),
            },
            "generic": {
                "path": os.path.join("anylog_api", "api_generic.py"),
                "functions": self.generic.list_commands()
            },
            # 2. Node state & health
            "node_status": {
                "path": os.path.join("anylog_api", "api_node_status.py"),
                "functions": self.node_status.list_commands(),
            },

            # 3. Data plane (what users usually care about)
            "data": {
                "path": os.path.join("anylog_api", "api_data.py"),
                "functions": self.data.list_commands(),
            },
            "data_aggregation": {
                "path": os.path.join("anylog_api", "api_data_aggregation.py"),
                "functions": self.data_aggregation.list_commands(),
            },
            "dbms": {
                "path": os.path.join("anylog_api", "api_dbms.py"),
                "functions": self.dbms.list_commands(),
            },

            # 4. Processing & orchestration
            "processes": {
                "path": os.path.join("anylog_api", "api_process.py"),
                "functions": self.processes.list_commands(),
            },
            "southbound": {
                "path": os.path.join("anylog_api", "api_southbound.py"),
                "functions": self.southbound.list_commands(),
            },

            # 5. System-level / infrastructure
            "blockchain": {
                "path": os.path.join("anylog_api", "api_blockchain.py"),
                "functions": self.blockchain.list_commands(),
            },
            "logging": {
                "path": os.path.join("anylog_api", "api_logs.py"),
                "functions": self.logging.list_commands(),
            },
        }

    def __help__(self):
        output = ""
        for cmd in self.modules:
            output += f"\n* [{cmd}]({self.modules.get(cmd).get('path')})"
            for func in self.modules.get(cmd).get('functions'):
                if ((cmd == "anylog_conn" and func in ["async_help", "help", "update_exec_mode", "async_get", "get",
                                                       "async_post",  "post", "async_put", "put"]) or
                        (cmd != "anylog_conn" and func != "list_commands" and self.modules.get(cmd).get('functions').get(func))):
                    output += f"\n\t* {func} - {self.modules.get(cmd).get('functions').get(func).split('\n')[1].capitalize()}"

        return output