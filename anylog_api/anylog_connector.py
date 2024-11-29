"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/
"""
import requests
from typing import Union

import anylog_api.__support__ as support

class AnyLogConnector:
    def __init__(self, conn:str, timeout:int=30):
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
        try:
            if support.check_conn_info(conn=conn) is True:
                self.conn, self.auth = support.separate_conn_info(conn=conn)
        except ValueError as e:
            raise ValueError(f"Invalid connection format: {conn}") from e

        try:
            self.timeout = int(timeout)
        except:
            raise ValueError(f'Timeout value must be of type int. Current format is {type(type)}')

    def get(self, headers:dict)->Union[requests.Response, bool, str]:
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
            r = requests.get(f'http://{self.conn}', headers=headers, auth=self.auth, timeout=self.timeout)
        except Exception as e:
            error = str(e)
            r = False
        else:
            if int(r.status_code) < 200 or int(r.status_code) > 299:
                error = int(r.status_code)
                r = False

        return r, error

    def put(self, headers:dict, payload:str)->Union[requests.Response, bool, str]:
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
            r = requests.put(f'http://{self.conn}', auth=self.auth, timeout=self.timeout, headers=headers,
                             data=payload)
        except Exception as e:
            error = str(e)
            r = False
        else:
            if int(r.status_code) < 200 or int(r.status_code) > 299:
                error = str(r.status_code)
                r = False

        return r, error

    def post(self, headers:dict, payload:str=None)->Union[requests.Response, bool, str]:
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
            r = requests.post(f'http://{self.conn}', headers=headers, data=payload, auth=self.auth,
                              timeout=self.timeout)
        except Exception as e:
            error = str(e)
            r = False
        else:
            if int(r.status_code) < 200 or int(r.status_code) > 299:
                error = str(r.status_code)
                r = False

        return r, error