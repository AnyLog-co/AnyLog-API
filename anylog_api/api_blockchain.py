import ast
import asyncio
import json

from anylog_api.anylog_rest_api import AnyLogRest
from anylog_api.support import ListCommands


class Blockchain(ListCommands):
    def __init__(self, anylog_conn:AnyLogRest):
        self.anylog_conn= anylog_conn


    def build_policy(self, policy_type:str, **kwargs):
        """
        builder for blockchain policy
        :args:
            policy_type:str - policy type
            **kwargs - used defined policies
        :params:
            new_policy:dict - generated policy
        :return:
            generated new policy
            if no content in kwargs, returns None
        """
        new_policy = None
        if kwargs:
            new_policy = {policy_type: {}}
            for name, value in kwargs.items():
                new_policy[policy_type][name] = value

        return new_policy


    async def async_insert_policy(self, policy, local:bool=True, master_node:str=None, blockchain:str=None,
                                  destination:str=None):
        """
        Insert blockchain policy
        :args:
            policy - policy to publish
            local:bool - store locally
            master_node:str - master node to store under
            blockchain:str - blockchain to store under
            destination:str - remote destination to send request against
        :params:
            new_policy:str - payload policy to publish
            headers:dict - REST headers
        """
        headers = {
            "command": "blockchain insert where policy=!new_policy and",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }
        headers["command"] += " local=true and" if local else " local=false and"
        headers["command"] += f" master={master_node} and" if master_node else ""
        headers["command"] += f" blockchain={blockchain} and" if blockchain else ""
        headers["command"] = headers["command"].rsplit(" and", 1)[0]

        new_policy = f"<new_policy={json.dumps(policy) if isinstance(policy, dict) else policy}>"

        await self.anylog_conn.async_post(headers=headers, payload=new_policy)

    def insert_policy(self, policy, local:bool=True, master_node:str=None, blockchain:str=None, destination:str=None):
        """
        Insert blockchain policy
        :args:
            policy - policy to publish
            local:bool - store locally
            master_node:str - master node to store under
            blockchain:str - blockchain to store under
            destination:str - remote destination to send request against
        :params:
            new_policy:str - payload policy to publish
            headers:dict - REST headers
        """
        asyncio.run(self.async_insert_policy(policy, local, master_node, blockchain, destination))


    async def async_blockchain_get(self, policy="*", where_conditions:str=None, bring_field:str=None,
                                   bring_conditions:str=None, destination:str=None):
        """
        Execute `blockchain get` against the blockchain
        :args:
            policy - comma separated list of  policy types to locate
            where_conditions:str - where conditions
            bring_field:str - bring field configs. Examples: 
            - first
            - last
            - ip_port
            - table
            - etc.
            bring_conditions:str - bring conditions
            destination:str - remote conn to send request
        :params:
            headers:dict - REST headers
        :return:
            result from `blockchain get`
        """
        headers = {
            "command": f"blockchain get",
            "User-Agent": "AnyLog/1.23",
            "destination": destination if destination else ""
        }

        policy = ast.literal_eval(policy)
        if isinstance(policy, list or tuple):
            policy = ",".join(policy)
        policy = policy.rsplit(',', 1)[0] if policy.strip().endswith(',') else policy

        headers["command"] += f" ({policy})"
        headers["command"] += f" where {where_conditions}" if where_conditions else ""
        headers["command"] += " bring" if bring_field or bring_conditions else ""
        headers["command"] += f".{bring_field}" if bring_field else  ""
        headers["command"] += f" {bring_conditions}" if bring_conditions else ""

        return self.anylog_conn.async_get(headers=headers)

    def blockchain_get(self, policy="*", where_conditions:str=None, bring_field:str=None,
                                   bring_conditions:str=None, destination:str=None):
        """
        Execute `blockchain get` against the blockchain
        :args:
            policy - comma separated list of  policy types to locate
            where_conditions:str - where conditions
            bring_field:str - bring field configs. Examples:
            - first
            - last
            - ip_port
            - table
            - etc.
            bring_conditions:str - bring conditions
            destination:str - remote conn to send request
        :params:
            headers:dict - REST headers
        :return:
            result from `blockchain get`
        """
        return asyncio.run(self.async_blockchain_get(policy, where_conditions, bring_field, bring_conditions,
                                                     destination))

