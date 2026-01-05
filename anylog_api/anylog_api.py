from anylog_api.anylog_rest_api import AnyLogRest
from backup.status import Status
from backup.logging import Logging
from backup.processes import  Processes

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

        # set api options
        self.help = self.anylog_conn.help
        self.node_status = Status(anylog_conn=self.anylog_conn)
        self.logging = Logging(anylog_conn=self.anylog_conn)
        self.processes = Processes(anylog_conn=self.anylog_conn)
        
        self.modules = {
            "node_status": self.node_status.list_commands(),
            "logging": self.logging.list_commands(),
            "processes": self.processes.list_commands()
        }


    def __help__(self):
        output = ""
        for cmd in self.modules:
            output += f"\n{cmd}"
            for func in self.modules[cmd]:
                if func != "list_commands" and self.modules[cmd][func]:
                    output += f"\n\t{func} - {self.modules[cmd][func].split('\n')[1].capitalize()}"

        return output