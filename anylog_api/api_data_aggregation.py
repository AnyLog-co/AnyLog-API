"""
Data
1. post / put data
3. query data
4. get data nodes
"""
import asyncio
import json

from anylog_api.anylog_rest_api import AnyLogRest
from anylog_api.api_dbms import DBMS
from anylog_api.support import ListCommands


class DataAggregation(ListCommands):
    def __init__(self, anylog_conn:AnyLogRest):
        self.anylog_conn = anylog_conn
        self.dbms_cmds = DBMS(anylog_conn=anylog_conn)

    async def async_full_aggregation_creation(self, db_name:str, table_name:str, value_column:str,
                                              db_type:str="sqlite", db_host:str|None=None, db_port:int|None=None,
                                              db_user:str|None=None, db_password:str|None=None,
                                              time_column:str="insert_timestamp", intervals:int=10,
                                              interval_time:str="1 minute", keep_aggregation:bool=False,
                                              target_dbms:str=None, target_table:str=None, destination:str|None=None):
        """
        Full process for configuring aggregations
        :process:
            1. if keep_aggregation
                - check / name target_dbms and target_table
                - list existing databases
                - connect to dbms if DNE
                - set partitioning for aggregation - if wanted (DNE)
                - set schedule to drop aggregation - if wanted (DNE)
            2. if value_column is "*" (all) then iterate through columns in tables
            3. declare aggregation
        args:
            db_name:str - logical database name
            table_name:str - logical table name
            value_column:str - column to aggregate against

            db_type:str - database to use
            host:str - IP address
            port:int - port
            user:str - database user
            password:str - password associated with user

            time_column:str - timestamp column to aggregate with
            intervals:int - number of aggregations to keep
            interval_time:str - time period for each interval
            keep_aggregation:bool - keep aggregations
            target_dbms:str - target database for aggregation
            target_table:str - target table for aggregation
            destination:str - remote node(s) to send request
        :params:
            columns:list - list of columns to be used to aggregation
        """

        # Step 1: Connect to logical database
        if keep_aggregation:
            target_dbms = target_dbms if target_dbms else f"agg_{db_name}"

            databases = await self.dbms_cmds.async_get_databases(json_frmt=True, destination=destination)
            if target_dbms not in databases:
                await self.dbms_cmds.connect_dbms(db_name=target_dbms, db_type=db_type, host=db_host, port=db_port,
                                                  user=db_user, password=db_password, destination=destination)

        # Step 2: generate list of columns
        if not value_column or value_column == "*":
            columns = []
            full_list = await self.dbms_cmds.async_get_columns(db_name=db_name, table_name=table_name, json_frmt=True,
                                                               destination=destination)
            for column in full_list:
                if column not in ["row_id", "tsd_id", "tsd_name"] and "timestamp" not in full_list.get(column):
                    columns.append(column)
                elif "timestamp" in full_list.get("column") and column != "insert_timestamp" and time_column == "insert_timestamp":
                    time_column = column
        else:
            columns = value_column.split(",")

        # Step 3: declare aggregation(s)
        for value_column in columns:
            target_table = target_table if target_table else f"{table_name.strip()}_{value_column.strip()}"
            await self.async_declare_aggregation(db_name, table_name, value_column, time_column, intervals,
                                                 interval_time, keep_aggregation, target_dbms, target_table,
                                                 destination)

    def full_aggregation_creation(self, db_name: str, table_name: str, value_column: str,
                                  db_type: str = "sqlite", db_host: str | None = None, db_port: int | None = None,
                                  db_user: str | None = None, db_password: str | None = None,
                                  time_column: str = "insert_timestamp", intervals: int = 10,
                                  interval_time: str = "1 minute", keep_aggregation: bool = False,
                                  target_dbms: str = None, target_table: str = None, destination: str | None = None):
        """
        Full process for configuring aggregations
        :process:
            1. if keep_aggregation
                - check / name target_dbms and target_table
                - list existing databases
                - connect to dbms if DNE
                - set partitioning for aggregation - if wanted (DNE)
                - set schedule to drop aggregation - if wanted (DNE)
            2. if value_column is "*" (all) then iterate through columns in tables
            3. declare aggregation
        args:
            db_name:str - logical database name
            table_name:str - logical table name
            value_column:str - column to aggregate against

            db_type:str - database to use
            host:str - IP address
            port:int - port
            user:str - database user
            password:str - password associated with user

            time_column:str - timestamp column to aggregate with
            intervals:int - number of aggregations to keep
            interval_time:str - time period for each interval
            keep_aggregation:bool - keep aggregations
            target_dbms:str - target database for aggregation
            target_table:str - target table for aggregation
            destination:str - remote node(s) to send request
        :params:
            columns:list - list of columns to be used to aggregation
        """
        asyncio.run(self.async_full_aggregation_creation(db_name, table_name, value_column, db_type, db_host, db_port,
                                                         db_user, db_password, time_column, intervals, interval_time,
                                                         keep_aggregation, target_dbms, target_table, destination))


    async def async_declare_aggregation(self, db_name:str, table_name:str, value_column:str,
                                        time_column:str="insert_timestamp", intervals:int=10,
                                        interval_time:str="1 minute", keep_aggregation:bool=False,
                                        target_dbms:str=None, target_table:str=None, destination:str|None=None):
        """
        Set aggregation on a specific table / column
        :args:
            db_name:str - logical database name
            table_name:str - logical table name
            value_column:str - column to aggregate against
            time_column:str - timestamp column to aggregate with
            intervals:int - number of aggregations to keep
            interval_time:str - time period for each interval
            keep_aggregation:bool - keep aggregations
            target_dbms:str - target database for aggregation
            target_table:str - target table for aggregation
            destination:str - remote node(s) to send request
        :params:
            headers:dict
        """
        command =  f"""set aggregation where 
            dbms={db_name} and 
            table={table_name} and 
            time_column={time_column} and
            value_column={value_column} and
            intervals={intervals} and
            time={interval_time}""".replace("\n", " ").replace("\t", " ").strip()
        if keep_aggregation:
            command += f"""
            and target_dbms={target_dbms if target_dbms else f'agg_{db_name}'}
            and target_table={target_table if target_table else f'{table_name.strip()}_{value_column.strip()}'} 
            """.replace("\n", " ").replace("\t", " ").strip()


        headers = {
            "command": command,
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        return await self.anylog_conn.async_post(headers)

    def declare_aggregation(self, db_name:str, table_name:str, value_column:str,
                            time_column:str="insert_timestamp", intervals:int=10,
                            interval_time:str="1 minute", keep_aggregation:bool=False,
                            target_dbms:str=None, target_table:str=None, destination:str|None=None):
        """
        Set aggregation on a specific table / column
        :args:
            db_name:str - logical database name
            table_name:str - logical table name
            value_column:str - column to aggregate against
            time_column:str - timestamp column to aggregate with
            intervals:int - number of aggregations to keep
            interval_time:str - time period for each interval
            keep_aggregation:bool - keep aggregations
            target_dbms:str - target database for aggregation
            target_table:str - target table for aggregation
            destination:str - remote node(s) to send request
        :params:
            headers:dict
        """
        asyncio.run(self.async_declare_aggregation(db_name, table_name, value_column, time_column, intervals,
                                                   interval_time, keep_aggregation, target_dbms, target_table, destination) )

    async def async_get_aggregation(self, db_name:str|None=None, table_name:str|None=None, value_column:str|None=None,
                                    json_format:bool=False, destination:str|None=None)->str|dict:
        """
        Get aggregation information
        :args:
            db_name:str - logical database name
            table_name:str - logical table name
            value_column:str - column to aggregate against
            json_format:bool - return content in JSON format
            destination:str - remote node(s) to send request against
        :params:
            headers:dict
        :return:
            aggregation information
        """
        command = "get aggregation"
        if db_name or json_format is True:
            command += " WHERE"
        if db_name:
            command += f" dbms={db_name} and"
            if table_name:
                command += f" table={table_name} and"
            if value_column:
                command += f" value_column={value_column} and"
        if json_format:
            command += " format=json and"
        headers = {
            "command": command.rsplit(" and", 1)[0].strip(),
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""

        }
        return await self.anylog_conn.async_post(headers)

    def get_aggregation(self, db_name:str|None=None, table_name:str|None=None, value_column:str|None=None,
                              json_format:bool=False, destination:str|None=None)->str|dict:
        """
        Get aggregation information
        :args:
            db_name:str - logical database name
            table_name:str - logical table name
            value_column:str - column to aggregate against
            json_format:bool - return content in JSON format
            destination:str - remote node(s) to send request against
        :params:
            headers:dict
        :return:
            aggregation information
        """
        return asyncio.run(self.async_get_aggregation(db_name, table_name, value_column, json_format, destination))

