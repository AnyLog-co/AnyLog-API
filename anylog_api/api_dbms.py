"""
connect dbms
get databases
get tables
get columns
"""
import asyncio

from anylog_api.anylog_rest_api import AnyLogRest
from anylog_api.support import ListCommands


class DBMS(ListCommands):
    def __init__(self, anylog_conn:AnyLogRest):
        self.anylog_conn = anylog_conn

    async def async_connect_dbms(self, db_name:str, db_type:str, host:str=None, port:int=None, user:str=None,
                                 password:str=None, autocommit:bool=False, in_memory:bool=False, destination:str=None):
        """
        Connect to logical database - for sqlite, psql and MongoDB
        :args:
            db_name:str - logical database name
            db_type:str - database to use
            host:str - IP address
            port:int - port
            user:str - database user
            password:str - password associated with user
            autocommit:bool
            in_memory:bool
            destination:str - remote destination to send request to
        :params:
            headers:dict - REST headers
        """
        if db_type not in ["sqlite", "psql", "mongo"]:
            raise ValueError(f"Unsupported db type ({db_type}) at this time")

        headers = {
            "command": f"connect dbms {db_name} where type={db_type} and",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        headers["command"] += f" ip={host} and" if host else ""
        headers["command"] += f" port={port} and" if port else ""
        headers["command"] += f" user={user} and" if user else ""
        headers["command"] += f" password={password} and" if password else ""
        if in_memory and db_type == "sqlite":
            headers["command"] += f" memory=true and"
        elif in_memory and db_type == "psql":
            headers["command"] += f" unlog=true and"
        if autocommit and db_type == "psql":
            headers["command"] += f" autocommit={autocommit} and"

        headers["command"] = headers["command"].rsplit(" and", 1)[0]

        await self.anylog_conn.async_post(headers=headers, payload=None)


    def connect_dbms(self, db_name:str, db_type:str, host:str=None, port:int=None, user:str=None,
                     password:str=None, autocommit:bool=False, in_memory:bool=False, destination:str=None):
        """
        Connect to logical database - for sqlite, psql and MongoDB
        :args:
            db_name:str - logical database name
            db_type:str - database to use
            host:str - IP address
            port:int - port
            user:str - database user
            password:str - password associated with user
            autocommit:bool
            in_memory:bool
            destination:str - remote destination to send request to
        :params:
            headers:dict - REST headers
        """
        asyncio.run(self.async_connect_dbms(db_name, db_type, host, port, user, password, autocommit, in_memory,
                                            destination))


    async def async_get_databases(self, json_frmt:bool=False, destination:str=None):
        """
        Get list of databases
        :args:
            json_frmt:bool - return results in JSON format
            destination:str - remote destination to send request to
        :params;
            headers:dict - REST headers
        :return;
            list of databases
        """
        headers = {
            "command": "get databsaes where format=json" if json_frmt else "get databases",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        return await self.anylog_conn.async_get(headers)

    def get_databases(self, json_frmt:bool=False, destination:str=None):
        """
        Get list of databases
        :args:
            json_frmt:bool - return results in JSON format
            destination:str - remote destination to send request to
        :params;
            headers:dict - REST headers
        :return;
            list of databases
        """
        return asyncio.run(self.async_get_databases(json_frmt, destination))


    async def async_get_tables(self, db_name:str, json_frmt:bool=False, destination:str=None):
        """
        get list of tables based on logical database name
        :args:
            db_name:str - logical database name
            json_frmt:bool - whether to return results in JSON format
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return;
            list of tables based on a logical database
        """
        headers = {
            "command": f"get tables where dbms={db_name} and format=json" if json_frmt else f"get tables where dbms={db_name}",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        return await self.anylog_conn.async_get(headers)

    def get_tables(self, db_name:str, json_frmt:bool=False, destination:str=None):
        """
        get list of tables based on logical database name
        :args:
            db_name:str - logical database name
            json_frmt:bool - whether to return results in JSON format
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return;
            list of tables based on a logical database
        """
        return asyncio.run(self.async_get_tables(db_name, json_frmt, destination))


    async def async_get_columns(self, db_name:str, table_name:str, json_frmt:bool=False, destination:str=None):
        """
        get list of columns based on logical database and table
        :args:
            db_name:str - logical database name
            table_name:str - logical table name
            json_frmt:bool - whether to return results in JSON format
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return;
            list of tables based on a logical database
        """
        headers = {
            "command": f"get columns where dbms={db_name} and table={table_name} and format=json" if json_frmt
            else f"get columns where dbms={db_name} and table={table_name}",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        return await self.anylog_conn.async_get(headers)

    def get_columns(self, db_name:str, table_name:str, json_frmt:bool=False, destination:str=None):
        """
        get list of columns based on logical database and table
        :args:
            db_name:str - logical database name
            table_name:str - logical table name
            json_frmt:bool - whether to return results in JSON format
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return;
            list of tables based on a logical database
        """
        return asyncio.run(self.async_get_columns(db_name, table_name, json_frmt, destination))

    async def async_get_data_nodes(self, json_frmt:bool=False, destination:str=None):
        """
        Get breakdown of data across the network
        :args:
            json_frmt:bool - return results in JSON format
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            results for `get data nodes`
        """
        headers = {
            "command": "get data nodes where format=json" if json_frmt else "get data nodes",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        return self.anylog_conn.async_get(headers)

    def get_data_nodes(self, json_frmt:bool=False, destination:str=None):
        """
        Get breakdown of data across the network
        :args:
            json_frmt:bool - return results in JSON format
            destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            results for `get data nodes`
        """
        return asyncio.run(self.get_data_nodes(json_frmt, destination))

