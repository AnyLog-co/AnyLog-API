import anylog_api.anylog_connector as anylog_connector
from anylog_api.__support__ import add_conditions
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.generic.get import get_help


def get_streaming(conn:anylog_connector.AnyLogConnector, json_format:bool=False, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False):
    """
    get streaming
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        json_format:bool - Set `get operator` output in JSON format
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        output - content returned
        headers:dict - REST headers
    :return:
        if return_cmd == True -- command to execute
        if view_help == True - None
        results for query
    """
    output = None
    headers = {
        "command": "get streaming",
        "User-Agent": "AnyLog/1.23"
    }

    if json_format is True:
        add_conditions(headers, format="json")

    if destination is not None:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return output


def get_data_nodes(conn:anylog_connector.AnyLogConnector, company_name:str=None, db_name:str=None, table_name:str=None,
                   sort:tuple=(), destination:str=None, view_help:bool=False, return_cmd:bool=False,
                   exception:bool=False):
    """
    get data nodes
    :args:
        conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        json_format:bool - Set `get operator` output in JSON format
        view_help:bool - get information about command
        return_cmd:bool - return command rather than executing it
        exception:bool - whether to print exception
    :params:
        output - content returned
        headers:dict - REST headers
    :return:
        if return_cmd == True -- command to execute
        if view_help == True - None
        results for query
    """
    output = None
    headers = {
        "command": "get data nodes",
        "User-Agent": "AnyLog/1.23"
    }

    add_conditions(headers, company=company_name, dbms=db_name, table=table_name, sort=sort)

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return output

