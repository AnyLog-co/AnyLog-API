"""
future:
- industrial
"""
import asyncio
from anylog_api.anylog_rest_api import AnyLogRest
from anylog_api.support import ListCommands


class Southbound(ListCommands):
    def __init__(self, anylog_conn:AnyLogRest):
        self.anylog_conn = anylog_conn

    async def async_run_msg_client(self, broker:str, port:int, topic:str, user:str=None, password:str=None,
                                   log:bool=False, policy_id:str=None,  db_name:str=None, table_name:str=None,
                                   mapping_configs:dict=None, destination:str=None):
        """
        Execute `run msg client` command
        :args:
            broker:str - broker IP
            port:int - broker port
            topic:str - message client topic
            user:str - message client user
            password:str - password associated with user
            log:bool - add logs in `run msg client`
        :mapping-args:
        * Option 1 - blockchain policy
            policy_id:str - blockchain policy id with mapping
        * Option 2 - manual mapping
            db_name:str - logical database name
            table_name:str  - logical table name
            mapping_configs:dict - mapping configurations for AnyLog
                {"column_name": {"value_type": [value type], "bring": [bring param]}}
                    -> {
                            "timestamp": {"value_type": "timestamp", "bring": "bring [ts]"},
                            "value": {"value_type": "int", "bring": "bring [value]"}
                        }
            destination:str - remote destination
        :params;
            headers:dict - REST header
        """
        headers = {
            "command": f"run msg client where broker={broker} and port={port} and",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }
        headers["command"] += f" user={user} and" if user else ""
        headers["command"] += f" password={password} and" if password else ""
        headers["command"] += f" log=true and" if log else " log=false and"
        headers["command"] += f" topic=(name={topic} and"
        if policy_id:
            headers["command"] += f" id={policy_id})"
        else:
            headers["command"] += f" dbms={db_name} and" if db_name else ""
            headers["command"] += f" table={table_name} and" if table_name else ""
            if mapping_configs:
                for key in mapping_configs:
                    value_type = mapping_configs.get(key).get("value_type")
                    if value_type not in ["str", "int", "float", "bool", "str"]:
                        value_type = "str"
                    bring = mapping_configs.get(key).get("bring")
                    if bring:
                        headers["command"] += f' column.{key}.{value_type}="{bring}" and'

        headers["command"] = headers["command"].rsplit("and", 1)[0] + ")"

        await self.anylog_conn.async_post(headers)

    def run_msg_client(self, broker:str, port:int, topic:str, user:str=None, password:str=None,
                       log:bool=False, policy_id:str=None,  db_name:str=None, table_name:str=None,
                       mapping_configs:dict=None, destination:str=None):
        """
        Execute `run msg client` command
        :args:
            broker:str - broker IP
            port:int - broker port
            topic:str - message client topic
            user:str - message client user
            password:str - password associated with user
            log:bool - add logs in `run msg client`
        :mapping-args:
        * Option 1 - blockchain policy
            policy_id:str - blockchain policy id with mapping
        * Option 2 - manual mapping
            db_name:str - logical database name
            table_name:str  - logical table name
            mapping_configs:dict - mapping configurations for AnyLog
                {"column_name": {"value_type": [value type], "bring": [bring param]}}
                    -> {
                            "timestamp": {"value_type": "timestamp", "bring": "bring [ts]"},
                            "value": {"value_type": "int", "bring": "bring [value]"}
                        }
            destination:str - remote destination
        :params;
            headers:dict - REST header
        """
        asyncio.run(self.async_run_msg_client(broker, port, topic, user, password, log, policy_id, db_name, table_name, mapping_configs, destination))

    async def async_get_msg_client(self, client_id:int=None, topic:str=None, destination:str=None):
        """
        Execute `get msg client`
        :args:
            client_id:str - msg client ID
            topic:str - specific topic
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            msg client information
        """
        headers = {
            "command": "get msg client where" if client_id or topic else "get msg client",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        if client_id:
            headers["command"] += f" id={client_id} and"
        if topic:
            headers["command"] += f" topic={topic} and"

        headers["command"] = headers["command"].rsplit(" and", 1)[0]

        return await self.anylog_conn.async_get(headers)

    def  get_msg_client(self, client_id:int=None, topic:str=None, destination:str=None):
        """
        Execute `get msg client`
        :args:
            client_id:str - msg client ID
            topic:str - specific topic
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            msg client information
        """
        return asyncio.run(self.async_run_msg_client(client_id, topic, destination))




