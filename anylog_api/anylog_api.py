from anylog_api.anylog_rest_api import AnyLogRest
from anylog_api.node_status import Status
from anylog_api.node_logging import Logging

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

        self.help = self.anylog_conn.help
        self.node_status = Status(anylog_conn=self.anylog_conn)
        self.logging = Logging(anylog_conn=self.anylog_conn)