import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.get import get_help
from anylog_api.generic.anylog_connector_support import extract_get_results
from anylog_api.anylog_connector_support import execute_publish_cmd


def connect_dbms(conn:anylog_connector.AnyLogConnector, db_name:str, db_type:str='sqlite', host:str=None, port:int=None,
                 user:str=None, password:str=None, memory:bool=False, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False):
    """
    Connect to logical database
    :args:
        conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database name
        db_type:str - physical database type
        host:str - database IP
        port:str - database Port
        user:str - user associated with database
        password:str - password associated with database
        memory:bool - run in memory
        destination:str - execute command remotely
        view_help:bool - whether to view help for command
        exception:bool - whether to print error messages
    """
    headers = {
        "command": f"connect dbms {db_name} where type={db_type}",
        "User-Agent": "AnyLog/1.23"
    }

    if host:
        headers['command'] += f" and ip={host}"
    if port:
        headers['command'] += f" and port={port}"
    if user:
        headers['command'] += f" and user={user}"
    if password:
        headers['command'] += f" and password={password}"
    if memory is True and db_name == 'sqlite':
        headers['command'] += f" and memory=true"

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def disconnect_dbms(conn:anylog_connector.AnyLogConnector, db_name:str, destination:str=None, view_help:bool=False,
                    return_cmd:bool=False, exception:bool=False):
    """
    Disconnect to logical database
    :args:
        conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database name
        destination:str - execute command remotely
        view_help:bool - whether to view help for command
        exception:bool - whether to print error messages
    :params:
        status:bool
        headers:dict - REST headers
    :return;
        status
    """
    headers = {
        "command": f"disconnect dbms {db_name}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def drop_dbms(conn:anylog_connector.AnyLogConnector, db_name:str, db_type:str='sqlite', host:str=None, port:int=None,
                 user:str=None, password:str=None, memory:bool=False, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False):
    """
    Disconnect logical database
    :args:
        conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database name
        db_type:str - physical database type
        host:str - database IP
        port:str - database Port
        user:str - user associated with database
        password:str - password associated with database
        memory:bool - run in memory
        destination:str - execute command remotely
        view_help:bool - whether to view help for command
        exception:bool - whether to print error messages
    """
    headers = {
        "command": f"drop dbms {db_name} from {db_type}",
        "User-Agent": "AnyLog/1.23"
    }

    if host or port or user or password:
        headers['command'] += " where "
    if host:
        headers['command'] += f"ip={host} and "
    if port:
        headers['command'] += f"port={port} and "
    if user:
        headers['command'] += f"user={user} and "
    if password:
        headers['command'] += f"password={password} and "
    if memory is True and db_name == 'sqlite':
        headers['command'] += f"memory=true"

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        staatus = headers['command']
    else:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def get_databases(conn:anylog_connectorAnyLogConnector, json_format:bool=False, destination:str=None,
                  view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Get list of databases
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/sql%20setup.md#the-get-databases-command
    :args:
        conn:AnyLogConnector - connection to AnyLog
        json_format:bool - whether to get results in JSON dictionary
        destination:str - execute command remotely
        view_help:bool - whether to view help for command
        exception:bool - whether to print error messages
    :params:
        output:str - results from REST request
        headers:dict - REST header requests
        r:request.get, error:str - REST request results
    :return:
        if success returns content (output), else None
    """
    output = None
    headers = {
        'command': 'get databases',
        'User-Agent': 'AnyLog/1.23'
    }

    if json_format is True:
        headers['command'] += ' where format=json'

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    else:
        output = extract_get_results(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return output


def check_db_exists(conn:AnyLogConnector, db_name:str, destination:str=None, view_help:bool=False, exception:bool=False):
    """
    check if database exists
    :args:
        conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database to view
        view_help:bool - whether to print help info for AnyLog command
        destination;bool - execute command remotely
        exception:bool - whether to print error messages
    :params:
        status:bool
        output:str - content from `get databases` request
    :return:
        exists True
        else False
    """
    status = False

    output = get_databases(conn=conn, json_format=True, view_help=view_help, destination=destination, exception=exception)
    if 'No DBMS connections found' not in output and output is not None:
        if db_name in list(output.keys()):
            status = True

    return status




