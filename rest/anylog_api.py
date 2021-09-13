import os
import requests
import __init__


class AnyLogConnect:
    def __init__(self, conn:str, auth:tuple=None, timeout:int=30):
        """
        The following are the base support for AnyLog via REST
            - GET: extract information from AnyLog (information + queries)
            - POST: Execute or POST command against AnyLog
            - POST_POLICY: POST information to blockchain
        :param:
            conn:str - REST connection info
            auth:tuple - Authentication information
            timeout:int - REST timeout
        """
        self.conn = conn
        self.auth = auth
        self.timeout = timeout

    def get(self, command:str, query:bool=False)->(str, str):
        """
        requests GET command
        :args:
            command:str - Command to execute
            query:bool - whether to query locally or against network
        :param:
            r:requests.response - response from requests
            error:str - If exception during error
            headers:dict - REST header
        :return:
            r, error
        """
        error = None
        headers = {
            'command': command,
            'User-Agent': 'AnyLog/1.23'
        }
        if query is True:
            headers['destination'] = 'network'

        try:
            r = requests.get('http://%s' % self.conn, headers=headers, auth=self.auth, timeout=self.timeout)
        except Exception as e:
            error = str(e)
            r = False

        return r, error

    def put_data(self, dbms:str, table:str, payloads:str)->(str, str):
        """
        Send data to AnyLog via PUT
        :sample payload:
            {'column1': 'column value', 'column2': 'column value', 'column3': 'column value'...}
        :args:
            dbms:str - database name
            table:str - table name
            payloads:str - payloads to send data to AnyLog
        :params:
            r:requests.response - response from requests
            error:str - error meessage
            headers:dict - REST headers
        :return:
            r, error
        """
        headers = {
            'type': 'json',
            'dbms': dbms,
            'table': table,
            'mode': 'file',
            'Content-Type': 'text/plain'
        }

        try:
            r = requests.put('http://%s' % self.conn, auth=self.auth, timeout=self.timeout, headers=headers, data=payloads)
        except Exception as e:
            error = str(e)
            r = False
        else:
            if int(r.status_code) != 200:
                error = int(r.status_code)
                r = False

        return r, error

    def post(self, command:str)->(str, str):
        """
        Generic POST command
        :args:
            command:str - command to execute
        :param:
            r:requests.response - response from requests
            error:str - If exception during error
            headers:dict - REST header info
        :return:
            r, error
        """
        error = None
        headers = {
            'command': command,
            'User-Agent': 'AnyLog/1.23'
        }
        try:
            r = requests.post('http://%s' % self.conn, headers=headers, auth=self.auth, timeout=self.timeout)
        except Exception as e:
            error = str(e)
            r = False
        else:
            if int(r.status_code) != 200:
                error = int(r.status_code)
                r = False

        return r, error

    def post_data (self, data:dict)->(str, str):
        """
        Send data to AnyLog via POST (requires MQTT on node receiving the data)
        :sample payload:
            {'dbms': 'db_name', 'table': 'table_name', 'column1': 'column value', 'column2': 'column value'...}
        :args:
            data:dict - data to send to Operator
        :params:
            r:requests.response - response from requests
            error:str - if exection during error
            headers:dict - headers for REST
            jdata:str - JSON conversion of data
        :return:
            r, error
        """
        error = None
        headers = {
            'command': 'data',
            'User-Agent': 'AnyLog/1.23',
            'Content-Type': 'text/plain'
        }
        try:
            r = requests.post('http://%s' % self.conn, auth=self.auth, timeout=self.timeout, headers=headers, data=data)
        except Exception as e:
            error = str(e)
            r = False
        else:
            if int(r.status_code) != 200:
                error = int(r.status_code)
                r = False

        return r, error

    def post_policy(self, policy:str, master_node:str)->(str, str):
        """
        POST to blockchain
        :link:
            https://github.com/AnyLog-co/documentation/blob/master/using%20rest.md#the-message-body-setups
        :args:
            policy:str - policy to POST to blockchain
            master_node:str - master node to post to
        :params:
            r:requests.response - response from requests
            error:str - If exception during error
            headers:dict - REST header info
            raw_data:str - data to POST
        :return:
            r, error
        """
        error = None
            headers = {
                "command": "blockchain push !policy",
                "destination": master_node,
                "Content-Type": "text/plain",
                "User-Agent": "AnyLog/1.23"
            }

        try:
            r = requests.post('http://%s' % self.conn, headers=headers, auth=self.auth, timeout=self.timeout, data=policy)
        except Exception as e:
            error = str(e)
            r = False
        else:
            if int(r.status_code) != 200:
                error = int(r.status_code)
                r = False

        return r, error
