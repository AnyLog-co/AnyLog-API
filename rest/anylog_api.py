import json 
import requests 

"""
""" 

class AnyLogConnect: 
    def __init__(self, conn:str, auth:tuple=None, timeout:int=30):
        """
        The folloowing are the base support for AnyLog via REST 
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
            error:str - If exception during error 
            headers:dict - REST header 
        :return: 
            result from REST request
            if fails - False, error
        """
        error = None 
        headers = {
            'command': command, 
            'User-Agent': 'AnyLog/1.23'
        } 
        if query == True: 
            headers['destination'] = 'network' 
    
        try: 
            r = requests.get('http://%s' % self.conn, headers=headers, auth=self.auth, timeout=self.timeout)
        except Exception as e: 
            error = str(e)  
            r = False 

        return r, error 

    def post(self, command:str)->(bool, str): 
        """
        Generic POST command
        :args: 
            command:str - command to execute 
        :param: 
            status:bool
            error:str - If exception during error 
            headers:dict - REST header info
        :return: 
            status, error
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


    def post_policy(self, policy:str, master_node:str)->(bool, str):
        """
        POST to blockchain 
        :args: 
            policy:str - policy to POST to blockchain
            master_node:str - master node to post to 
        :params: 
            status:bool 
            error:str - If exception during error
            headers:dict - REST header info
            raw_data:str - data to POST 
        :return: 
            status, error
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
            if r.status_code != 200: 
                error = int(r.status_code)
                r = False 

        return r, error
