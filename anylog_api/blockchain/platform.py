import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.anylog_connector_support import execute_publish_cmd, extract_get_results


def connect_platform(conn:anylog_connector.AnyLogConnector, platform:str, provider:str, contract:str=None,
                     private_key:str=None, public_key:str=None, gas_read:float=None, gas_write:float=0,
                     destination:str="", view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    output = None
    headers = {
        "command": f"blockchain connect to {platform} where provider={provider}",
        "User-Agent": "AnyLog/1.23"
    }

    if contract:
        headers['command'] += f" and contract={contract}"
    if private_key and public_key:
        headers['command'] += f" and private_key={private_key} and public_key={public_key}"
    if gas_read:
        headers['command'] += f" and gas_read={gas_read}"
    if gas_write:
        headers['command'] += f" and gas_write={gas_write}"

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = execute_publish_cmd(conn=conn, cmd="POST", headers=headers, payload=None, exception=exception)

    return output


def create_account(conn:anylog_connector.AnyLogConnector, platform:str, destination:str="", view_help:bool=False,
                   return_cmd:bool=False, exception:bool=False):
    output = None
    headers = {
        "command": f"blockchain create account {platform}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = execute_publish_cmd(conn=conn, cmd="POST", headers=headers, payload=None, exception=exception)

    return output


def set_account(conn:anylog_connector.AnyLogConnector, platform:str, private_key:str, public_key:str,
                chain_id:str, destination:str="", view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    output = None
    headers = {
        "command": f"blockchain set account info where platform={platform} and private_key={private_key} and public_key={public_key} and chain_id={chain_id}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = execute_publish_cmd(conn=conn, cmd="POST", headers=headers, payload=None, exception=exception)

    return output


def deploy_contract(conn:anylog_connector.AnyLogConnector, platform:str, public_key:str, destination:str="",
                    view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    output = None
    headers = {
        "command": f"blockchain deploy contract where  platform={platform} and public_key={public_key}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = execute_publish_cmd(conn=conn, cmd="POST", headers=headers, payload=None, exception=exception)

    return output


def set_account_info(conn:anylog_connector.AnyLogConnector, platform:str, contract:str, destination:str="",
                    view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    output = None
    headers = {
        "command": f"blockchain set account info where platform={platform} and contract={contract}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = execute_publish_cmd(conn=conn, cmd="POST", headers=headers, payload=None, exception=exception)

    return output


def blockchain_checkout(conn:anylog_connector.AnyLogConnector, platform:str, destination:str="", view_help:bool=False,
                        return_cmd:bool=False, exception:bool=False):
    output = None
    headers = {
        "command": f"blockchain checkout from {platform}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = execute_publish_cmd(conn=conn, cmd="POST", headers=headers, payload=None, exception=exception)

    return output

def view_platform(conn:anylog_connector.AnyLogConnector, destination:str="", view_help:bool=False, return_cmd:bool=False,
                  exception:bool=False):
    output = None
    headers = {
        "command": "get platforms",
        "User-Agent": "AnyLog/1.23"
    }
    if destination:
        headers['destination'] = destination
    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output

