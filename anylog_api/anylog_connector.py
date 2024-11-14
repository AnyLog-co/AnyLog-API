"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""

import requests

class AnyLogConnector:
    def __init__(self, conn:str, auth:tuple=None, timeout:int=30):
        """
        The following are the base support for AnyLog via REST
            - GET: extract information from AnyLog (information + queries)
            - POST: Execute or POST command against AnyLog
            - POST_POLICY: POST information to blockchain
        :url:
            https://github.com/AnyLog-co/documentation/blob/master/using%20rest.md
        :param:
            conn:str - REST connection info
            auth:tuple - Authentication information
            timeout:int - REST timeout
        """
        self.conn = conn
        self.auth = auth
        if self.auth is None:
            self.auth = ()
        self.timeout = timeout

    def get(self, headers:dict)->(str, str):
        """
        requests GET command
        :args:
            headers:dict - header to execute
        :param:
            r:requests.response - response from requests
            error:str - If exception during error
        :return:
            r, error
        """
        error = None

        try:
            r = requests.get('http://%s' % self.conn, headers=headers, auth=self.auth, timeout=self.timeout)
        except Exception as e:
            error = str(e)
            r = False
        else:
            if int(r.status_code) < 200 or int(r.status_code) > 299:
                error = int(r.status_code)
                r = False

        return r, error

    def put(self, headers:dict, payload:str):
        """
        Execute a PUT command against AnyLog - mainly used for Data
        :args:
            headers:dict - header to execute
        :param:
            r:requests.response - response from requests
            error:str - If exception during error
        :return:
            r, error
        """
        error = None
        try:
            r = requests.put('http://%s' % self.conn, auth=self.auth, timeout=self.timeout, headers=headers,
                             data=payload)
        except Exception as e:
            error = str(e)
            r = False
        else:
            if int(r.status_code) < 200 or int(r.status_code) > 299:
                error = str(r.status_code)
                r = False

        return r, error

    def post(self, headers:dict, payload:str=None):
        """
        Execute POST command against AnyLog. payload is required under the following conditions:
            1. payload can be data that you want to add into AnyLog, in which case you should also have an
                MQTT client of type REST running on said node
            2. payload can be a policy you'd like to add into the blockchain
            3. payload can be a policy you'd like to remove from the blockchain
                note only works with Master, cannot remove a policy on a real blockchain like Ethereum.
        :args:
            headers:dict - request headers
            payloads:str - data to post
        :params:
            r:requests.response - response from requests
            error:str - If exception during error
        :return:
            r, error
        """
        error = None
        try:
            r = requests.post('http://%s' % self.conn, headers=headers, data=payload, auth=self.auth,
                              timeout=self.timeout)
        except Exception as e:
            error = str(e)
            r = False
        else:
            if int(r.status_code) < 200 or int(r.status_code) > 299:
                error = str(r.status_code)
                r = False

        return r, error

