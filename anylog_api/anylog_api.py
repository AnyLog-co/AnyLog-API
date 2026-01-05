from anylog_api.anylog_rest_api import AnyLogRest
from anylog_api.api_node_status import Status
from anylog_api.api_logs import Logging
from anylog_api.api_process import Processes
from anylog_api.api_blockchain import Blockchain


class AnyLogAPI:
    def __init__(self, conn:str, auth:tuple=None, connection_timeout:float=30, read_timeout:float=30,
                 write_timeout:float=30):
        """
        "main" for AnyLlog API
        :params:
            self.anylog_conn -
        """
        self.anylog_conn = AnyLogRest(conn=conn, auth=auth, connection_timeout=connection_timeout,
                                      read_timeout=read_timeout, write_timeout=write_timeout)

        # API configurations
        self.help = self.anylog_conn.help
        self.exec_mode = self.anylog_conn.exec_mode
        self.update_exec_mode = self.anylog_conn.update_exec_mode

        # Functions
        self.node_status = Status(anylog_conn=self.anylog_conn)
        self.logging = Logging(anylog_conn=self.anylog_conn)
        self.processes = Processes(anylog_conn=self.anylog_conn)
        self.blockchain = Blockchain(anylog_conn=self.anylog_conn)

        # Help
        self.modules = {
            "anylog_conn": self.anylog_conn.list_commands(),
            "node_status": self.node_status.list_commands(),
            "logging": self.logging.list_commands(),
            "processes": self.processes.list_commands(),
            "blockchain": self.blockchain.list_commands()
        }


    def __help__(self):
        output = ""
        for cmd in self.modules:
            output += f"\n{cmd}"
            for func in self.modules[cmd]:
                if ((cmd == "anylog_conn" and func in ["help", "update_exec_mode"]) or
                        (cmd != "anylog_conn" and func != "list_commands" and self.modules[cmd][func])):
                    output += f"\n\t{func} - {self.modules[cmd][func].split('\n')[1].capitalize()}"

        return output