from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.generic_get_cmd import get_help
from anylog_api_py.rest_support import print_rest_error, extract_results
from anylog_api_py.support import dict_to_string



def get(anylog_conn:AnyLogConnector, policy_types:list=["*"], where_conditions:list=[], bring_conditions:str="",
        separator:str="", destination:str=None, cmd_explain:bool=False, exception:bool=False):
    """
    Execute blockchain get command
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/blockchain%20commands.md#query-policies
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog node
        policy_types:list - policy types to look for
        where_conditions:list - where conditions
        bring_conditions:list - bring conditions
        separator:str - bring separator
        destination:str - destination IP:PORT
        cmd_explain:bool - call help command instead of execute query
        exception:bool - whether to print exceptions or not
    :params:
        output - results from REST request
        header:dict - REST headers
    :return:
        output, None if fails
    """
    output = None
    headers = {
        "command": "blockchain get ",
        "User-Agent": "AnyLog/1.23",
        "destination": destination
    }

    if cmd_explain is True:
        return get_help(anylog_conn=anylog_conn, cmd=headers["command"], exception=exception)

    if isinstance(policy_types, list):
        for policy_type in policy_types:
            headers["command"] += policy_type
            if policy_type != policy_types[-1]:
                headers["command"] += ", "
    else:
        headers["command"] += policy_types

    if isinstance(where_conditions, list) and where_conditions != []:
        headers["command"] += " where "
        for where_condition in where_conditions:
            headers["command"] += where_condition
            if where_condition != where_conditions[-1]:
                headers["command"] += " and "
    elif where_conditions != "" and where_conditions is not None:
        headers["command"] += f" where {where_conditions}"

    if bring_conditions != "" and bring_conditions is not None:
        headers["command"] += f" bring {bring_conditions}"

    if separator != "" and separator is not None:
        headers["command"] += f" separator={separator}"

    r, error = anylog_conn.get(headers=headers)
    if r is False and exception is True:
        print_rest_error(call_type='GET', cmd=headers['command'], error=error)
    elif r is not False:
        output = extract_results(cmd=headers['command'], r=r, exception=exception)
    return output


def declare_policy(anylog_conn:AnyLogConnector, policy:str, destination:str=None, cmd_explain:bool=False,
                   exception:bool=False):
    """
    Declare a policy on the blockchain
    :args:
       anylog_conn:AnyLogConnector - connection to AnyLog node
       policy:str - policy to decalre on the blockchain
       destination:str - destination IP:PORT (should be connectivity to Master node)
       cmd_explain:bool - call help command instead of execute query
       exception:bool - whether to print exceptions or not
    :params:
    """
    pass