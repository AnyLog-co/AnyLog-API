import asyncio
from anylog_api.anylog_rest_api import AnyLogRest
from anylog_api.list_cmds import ListCommands


class Processes(ListCommands):
    def __init__(self, anylog_conn:AnyLogRest):
        self.anylog_conn = anylog_conn

    async def async_get_processes(self, json_frmt:bool=False, destination:str=None):
        """
        get status of AnyLog processes
        :args:
            json_frmt:bool - JSON format
           destination:str - remote destination
        :params:
            headers:dict - REST headers
        :return:
            processes running on AnyLog and whether they're running
        """
        headers = {
            "command": "get processes where format=json" if json_frmt else "get processes",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        return await self.anylog_conn.async_get(headers=headers)

    def get_processes(self, json_frmt:bool=False, destination:str=None):
        """
        get status of AnyLog processes
        :args:
            json_frmt:bool - JSON format
           destination:str - remote destination
        :params:
            headers:dict - REST header
        :return:
            processes running on AnyLog and whether they're running
        """
        return asyncio.run(self.async_get_processes(json_frmt, destination))

    async def async_run_operator(self, policy:str, create_table:bool=True, update_tsd_info:bool=True, archive_json:bool=True,
                                 archive_sql:bool=True, compress_json:bool=True, compress_sql:bool=True,
                                 master_node:str=None, blockchain_conn:str=None, destination:str=None):
        """
        Execute `run operator` to insert data
        :args;
            policy:str - Operator node Policy ID
            compress_json:bool - True/False to enable/disable compression of the JSON file.
            compress_sql:bool - True/False to enable/disable compression of the SQL file.
            archive_json:bool - True moves the JSON file to the 'archive' dir if processing is successful. The file deleted if archive_sql is false.
            archive_sql:bool -  True moves the SQL file to the 'archive' dir if processing is successful. The file deleted if archive_sql is false.
            create_table:bool - A True value creates a table if the table doesn't exist.
            master_node - The IP and Port of a Master Node (if a master node is used).
            update_tsd_info:bool - True/False to update a summary table (tsd_info table in almgm dbms) with status of files ingested.
            blockchain_conn:str - blockchain connection
        :params:
            headers:dict - REST headers
        """
        if not policy:
            raise ValueError(f'Missing operator policy ID')

        headers = {
            "command": f"run operator where policy={policy} and",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        headers["command"] += " create_table=true and" if create_table else " create_table=false and"
        headers["command"] += " update_tsd_info=true and" if update_tsd_info else " update_tsd_info=false and"
        headers["command"] += " archive_json=true and" if archive_json else " archive_json=false and"
        headers["command"] += " archive_sql=true and" if archive_sql else " archive_sql=false and"
        headers["command"] += " compress_json=true and" if compress_json else " compress_json=false and"
        headers["command"] += " compress_sql=true and" if compress_sql else " compress_sql=false and"
        if master_node:
            headers["command"] += f" master_node={master_node}"
        if blockchain_conn:
            headers["command"] += f" blockchain={blockchain_conn}"

        await self.anylog_conn.async_post(headers=headers)


    def run_operator(self, policy:str, create_table:bool=True, update_tsd_info:bool=True, archive_json:bool=True,
                                 archive_sql:bool=True, compress_json:bool=True, compress_sql:bool=True,
                                 master_node:str=None, blockchain_conn:str=None, destination:str=None):
        """
        Execute `run operator` to insert data
        :args;
            policy:str - Operator node Policy ID
            compress_json:bool - True/False to enable/disable compression of the JSON file.
            compress_sql:bool - True/False to enable/disable compression of the SQL file.
            archive_json:bool - True moves the JSON file to the 'archive' dir if processing is successful. The file deleted if archive_sql is false.
            archive_sql:bool -  True moves the SQL file to the 'archive' dir if processing is successful. The file deleted if archive_sql is false.
            create_table:bool - A True value creates a table if the table doesn't exist.
            master_node - The IP and Port of a Master Node (if a master node is used).
            update_tsd_info:bool - True/False to update a summary table (tsd_info table in almgm dbms) with status of files ingested.
            blockchain_conn:str - blockchain connection
        :params:
            headers:dict - REST headers
        """
        asyncio.run(self.async_run_operator(policy, create_table, update_tsd_info, archive_json, archive_sql,
                                            compress_json, compress_sql, master_node, blockchain_conn, destination))


    async def async_run_publisher(self):
        pass

    def run_publisher(self):
        pass

    async def async_get_operator(self):
        pass

    def get_operator(self):
        pass

    async def async_get_publisher(self):
        pass

    def get_publisher(self):
        pass

