"""
Data
1. post / put data
3. query data
4. get data nodes
"""
import asyncio

from anylog_api.anylog_rest_api import AnyLogRest
from anylog_api.support import ListCommands


class Data(ListCommands):
    def __init__(self, anylog_conn:AnyLogRest):
        self.anylog_conn = anylog_conn


    def sql_request_builder(self, db_name:str, query:str, output_format:str="json", stats:bool=True, include:str=None,
                            extend:str=None, timezone:str=None):
        """
        Create a complete SQL command for AnyLog / EdgeLake
        :args:
            db_name:str - logical database name
            query:str - SELECT / query statement
            output_format:str - output format
            stats:bool - include status in response
            include:str - comma separated table(s) to include in request
            extend:str - comma separated param(s) to include in request
            timezone:str - timezone
        :params:
            command:str - generated command
        :return:
            command
        """
        include = ','.join(include) if isinstance(include, tuple or list) else include
        extend = ','.join(extend) if isinstance(extend, tuple or list) else extend
        command = f"sql {db_name}"
        command += f" format={output_format} and" if output_format in ["json", "table", "json:list"] else ""
        command += f" stat=true and" if stats else " stat=false and"
        command += f" include=({include}) and" if include else ""
        command += f" extend=({extend}) and" if extend else ""
        command += f" timezone={timezone} and" if timezone else ""

        return command.rsplit(" and", 1)[0] + f'"{query}"'


    async def async_query(self, request_stmt:str=None, db_name:str=None, query:str=None, output_format:str="json",
                          stats:bool=True, include:str=None, extend:str=None, timezone:str=None,
                          destination:str="network"):
        """
        Execute query request against the network
        :args:
            request_stmt:str - user's pre-defined request statement
            - or utilizing sql_request_builder -
            db_name:str - logical database name
            query:str - SELECT / query statement
            output_format:str - output format
            stats:bool - include status in response
            include:str - comma separated table(s) to include in request
            extend:str - comma separated param(s) to include in request
            timezone:str - timezone

            destination:str - remote node(s) to send request against
        :params:
            headers:dict
        :return:
            query request results
        """
        if not request_stmt and (not db_name or not query):
            return None
        elif not request_stmt and db_name and query:
            request_stmt = self.sql_request_builder(db_name, query, output_format, stats, include, extend, timezone)

        headers = {
            "command": request_stmt,
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        return await self.anylog_conn.async_get(headers)


    def query(self, request_stmt:str=None, db_name:str=None, query:str=None, output_format:str="json",
              stats:bool=True, include:str=None, extend:str=None, timezone:str=None,
              destination:str="network"):
        """
        Execute query request againsts the network
        :args:
            request_stmt:str - user's pre-defined request statement
            - or utilizing sql_request_builder -
            db_name:str - logical database name
            query:str - SELECT / query statement
            output_format:str - output format
            stats:bool - include status in response
            include:str - comma separated table(s) to include in request
            extend:str - comma separated param(s) to include in request
            timezone:str - timezone

            destination:str - remote node(s) to send request against
        :params:
            headers:dict
        :return:
            query request results
        """
        return asyncio.run(self.async_query(request_stmt, db_name, query, output_format, stats, include, extend,
                                            timezone, destination))

    async def async_post_data(self, topic:str, payload, content_type:str="text/plain"):
        """
        Publish data into AnyLog / EdgeLake via POST
        :args:
            topic:str - msg client topic to be used for mapping
            payload - content to publish
            content_type:str - content type to publish
        :params:
            headers:dict - REST headers
        """
        headers = {
            "command": "data",
            "topic": topic,
            "User-Agent": "AnyLog/1.23",
            "Content-Type": content_type
        }

        await self.anylog_conn.async_post(headers=headers, payload=payload)

    def post_data(self, topic:str, payload, content_type:str="text/plain"):
        """
        Publish data into AnyLog / EdgeLake via POST
        :args:
            topic:str - msg client topic to be used for mapping
            payload - content to publish
            content_type:str - content type to publish
        :params:
            headers:dict - REST headers
        """
        asyncio.run(self.async_post_data(topic, payload, content_type))


    async def async_put_data(self, db_name:str, table_name:str, payload, mode:str="streaming",
                             content_type:str="text/plain"):
        """
        Publish content into AnyLog / EdgeLake via PUT
        :args:
            db_name:str - logical database name
            table_name:str - logical table name
            payload - content to publish
            mode:str - whether to PUT data continuously (streaming) or one at a time (file)
            content_type:str - content type to publish
        :params:
            headers:dict - REST headers
        """
        headers = {
            "dbms": db_name,
            "table": table_name,
            "mode": mode if mode in ["streaming", "file"] else "streaming",
            "User-Agent": "AnyLog/1.23",
            "Content-Type": content_type
        }
        await self.anylog_conn.async_put(headers, payload)

    def put_data(self, db_name:str, table_name:str, payload, mode:str="streaming",
                             content_type:str="text/plain"):
        """
        Publish content into AnyLog / EdgeLake via PUT
        :args:
            db_name:str - logical database name
            table_name:str - logical table name
            payload - content to publish
            mode:str - whether to PUT data continuously (streaming) or one at a time (file)
            content_type:str - content type to publish
        :params:
            headers:dict - REST headers
        """
        asyncio.run(self.async_put_data(db_name, table_name, payload, mode, content_type))